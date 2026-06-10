#!/usr/bin/env python3
"""Validation GUI for trsproc transcription review.

Provides a PyQt6-based graphical interface for reviewing and validating
transcription segments with audio playback, error counting, and progress
tracking. The main entry point is :class:`TranscriptionValidatorGUI`.
"""

from __future__ import annotations

import shutil

import pandas as pd
from PyQt6.QtCore import QSignalBlocker, Qt, QUrl
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from trsproc.validation.io import (
    COL_ERR_SEG,
    COL_ERR_TRANS,
    COL_FILE,
    COL_SEG,
    COL_TRANS,
    COL_VALIDATED,
    compute_totals,
    load_validation_tsv,
    save_validated_tsv_atomic,
)


class DirtyAction:
    """Constants for dirty-state handling during navigation.

    Attributes:
        CLEAN: No unsaved changes.
        SAVED: Changes were saved by the user.
        DISCARDED: Changes were discarded.
        CANCELLED: The operation was cancelled.
    """

    CLEAN = "clean"
    SAVED = "saved"
    DISCARDED = "discarded"
    CANCELLED = "cancelled"


APP_BG = "#F5F6F8"
PANEL_BG = "#FFFFFF"
BORDER = "#E0E3E7"
TEXT = "#333333"

COMMON_BUTTON_STYLE = """
QPushButton {
    background-color: #F2F3F5;
    border: 1px solid #DADDE1;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
    color: #333333;
}
QPushButton:hover { background-color: #E8EAED; }
QPushButton:pressed { background-color: #DDE1E6; }
QPushButton:disabled {
    background-color: #F2F3F5;
    color: #9AA0A6;
    border: 1px solid #E6E8EB;
}
"""

PRIMARY_BUTTON_STYLE = """
QPushButton {
    background-color: #E7ECF5;
    border: 1px solid #C9D2E3;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
    color: #2F3A4A;
}
QPushButton:hover { background-color: #DCE3F0; }
QPushButton:pressed { background-color: #CFD9EA; }
QPushButton:disabled {
    background-color: #EEF2F8;
    color: #8B93A1;
    border: 1px solid #DCE3F0;
}
"""

ICON_BUTTON_STYLE = """
QPushButton {
    background-color: #F2F3F5;
    border: 1px solid #DADDE1;
    border-radius: 6px;
    padding: 0px;
    font-size: 18px;
    font-weight: 700;
    color: #333333;
    text-align: center;
}
QPushButton:hover { background-color: #E8EAED; }
QPushButton:pressed { background-color: #DDE1E6; }
QPushButton:disabled {
    background-color: #F2F3F5;
    color: #9AA0A6;
    border: 1px solid #E6E8EB;
}
"""

LIST_STYLE = f"""
QListWidget {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    outline: none;
}}
QListWidget::item {{
    padding: 6px 8px;
    border: none;
}}
QListWidget::item:selected {{
    background-color: #EEF1F5;
    color: {TEXT};
    border: none;
}}
QListWidget::item:focus {{ outline: none; }}
"""

SEEK_BAR_STYLE = """
QSlider::groove:horizontal {
    height: 4px;
    background: #F0F0EE;
}
QSlider::sub-page:horizontal { background: #D2D8E0; }
QSlider::handle:horizontal {
    background: #D2D8E0;
    width: 10px;
    margin: -4px 0;
    border-radius: 5px;
}
"""

TRANSCRIPT_STYLE = """
font-family: 'DejaVu Sans Mono';
font-size: 16px;
background-color: #FDFDFD;
padding: 10px;
border: 1px solid #DDD;
color: #333333;
"""


def format_ms(ms):
    """Convert a duration in milliseconds to a ``MM:SS`` formatted string.

    Args:
        ms: Duration in milliseconds.

    Returns:
        A string in ``"MM:SS"`` format, or ``"00:00"`` if the input is invalid.
    """
    if ms is None or ms < 0:
        return "00:00"
    sec = ms // 1000

    return f"{sec // 60:02d}:{sec % 60:02d}"


class ClickableSlider(QSlider):
    """A QSlider that responds to mouse clicks to jump to a position."""

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse press events to allow click-to-seek behavior.

        Computes the slider ratio from the click position and sets the value
        accordingly.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.orientation() == Qt.Orientation.Horizontal:
                ratio = event.position().x() / max(1, self.width())
            else:
                ratio = 1.0 - (event.position().y() / max(1, self.height()))

            ratio = max(0.0, min(1.0, ratio))
            new_value = int(self.minimum() + ratio * (self.maximum() - self.minimum()))
            self.setValue(new_value)
            self.sliderMoved.emit(new_value)
            event.accept()
            return
        super().mousePressEvent(event)


class TranscriptionValidatorGUI(QWidget):
    """PyQt6 GUI for validating audio transcription segments.

    Displays a segment list, transcript viewer, audio player, and error
    counters. Supports keyboard shortcuts for efficient navigation.

    Hotkeys:
        - ``Space``: Play / Pause
        - ``R``: Replay from start
        - ``Enter``: Save and Next
        - ``Left / Right``: Segment errors -1 / +1
        - ``Down / Up``: Transcript errors -1 / +1
    """

    def __init__(self, paths):
        """Initialize the validation GUI.

        Args:
            paths: A :class:`~trsproc.validation.io.ValidationPaths` instance
                containing the input TSV path, audio directory, and output path.

        Raises:
            FileNotFoundError: If the input TSV file does not exist.
        """
        super().__init__()
        self.paths = paths

        if not self.paths.input_path.exists():
            raise FileNotFoundError(f"TSV not found: {self.paths.input_path}")

        self.df: pd.DataFrame = load_validation_tsv(self.paths.input_path)
        self.current_index = 0
        self.dirty = False
        self._is_user_seeking = False
        self._init_ui()

    def _init_ui(self):
        """Build and initialize the main window layout.

        Sets up the left/right panels, populates the segment list, and
        connects signal/slot handlers. Shows an information dialog if the
        data is empty.
        """
        self.setWindowTitle("Audio Transcription Validation Tool")
        self.resize(1050, 550)
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter)

        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([340, 710])

        self._init_shortcuts()
        self._populate_list()
        self.list_widget.currentRowChanged.connect(self.jump_to_index)

        if len(self.df) == 0:
            QMessageBox.information(self, "Empty file", "No data rows found.")
            self._set_controls_enabled(False)
            return

        self._refresh_ui()
        self.list_widget.blockSignals(True)
        self.list_widget.setCurrentRow(self.current_index)
        self.list_widget.blockSignals(False)

        return

    def _build_left_panel(self):
        """Create the segment list panel.

        Returns:
            A :class:`QListWidget` styled for segment navigation.
        """
        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(320)
        self.list_widget.setStyleSheet(LIST_STYLE)

        return self.list_widget

    def _build_right_panel(self):
        """Create the right-side validation controls panel.

        Returns:
            A :class:`QWidget` containing the header, transcript viewer,
            audio player, error counters, and navigation buttons.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addLayout(self._build_header())
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet("color: #B71C1C;")
        layout.addWidget(self.hint_label)
        layout.addLayout(self._build_transcript())
        layout.addLayout(self._build_player())
        layout.addSpacing(10)
        layout.addLayout(self._build_counters())
        layout.addSpacing(16)
        layout.addLayout(self._build_nav())

        return widget

    def _build_header(self):
        """Create the progress and file-info header.

        Returns:
            A :class:`QHBoxLayout` with progress status and current file labels.
        """
        layout = QHBoxLayout()
        self.status_label = QLabel("")
        self.file_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: 600; color: #333333;")
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.file_label)

        return layout

    def _build_transcript(self):
        """Create the transcript text viewer.

        Returns:
            A :class:`QVBoxLayout` with a label and a read-only
            :class:`QTextBrowser` for displaying the current transcript.
        """
        layout = QVBoxLayout()
        label = QLabel("Transcript:")
        label.setStyleSheet("font-size: 14px; font-weight: 600; color: #333333;")
        layout.addWidget(label)
        self.transcript_view = QTextBrowser()
        self.transcript_view.setStyleSheet(TRANSCRIPT_STYLE)
        self.transcript_view.setMinimumHeight(220)
        layout.addWidget(self.transcript_view)

        return layout

    def _build_player(self):
        """Create the audio playback section.

        Returns:
            A :class:`QVBoxLayout` containing the media player buttons,
            seek slider, and time label.
        """
        layout = QVBoxLayout()

        self._init_media_player()
        layout.addLayout(self._build_player_buttons())
        layout.addWidget(self._build_seek_slider())
        layout.addWidget(self._build_time_label())
        self._connect_player_signals()

        return layout

    def _init_media_player(self):
        """Initialize the QMediaPlayer and QAudioOutput for audio playback."""
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)

        return

    def _build_player_buttons(self):
        """Create the playback control buttons.

        Returns:
            A :class:`QHBoxLayout` with Play, Pause, and Replay buttons.
        """
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.replay_btn = QPushButton("↻")

        for btn in (self.play_btn, self.pause_btn, self.replay_btn):
            btn.setMinimumHeight(45)
            btn.setStyleSheet(ICON_BUTTON_STYLE)
            btn_row.addWidget(btn, 1)

        self.play_btn.clicked.connect(self.play_audio)
        self.pause_btn.clicked.connect(self.pause_audio)
        self.replay_btn.clicked.connect(self.replay_audio)

        return btn_row

    def _build_seek_slider(self):
        """Create the seek/progress slider.

        Returns:
            A :class:`ClickableSlider` configured for horizontal audio seeking.
        """
        self.position_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.setEnabled(False)
        self.position_slider.setStyleSheet(SEEK_BAR_STYLE)

        return self.position_slider

    def _build_time_label(self):
        """Create the playback time display label.

        Returns:
            A :class:`QLabel` showing the current position and total duration.
        """
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #555;")

        return self.time_label

    def _connect_player_signals(self):
        """Connect media player and slider signals to their handlers.

        Wires ``durationChanged``, ``positionChanged``, and slider events
        to the corresponding slot methods.
        """
        self.media_player.durationChanged.connect(self._on_duration_changed)
        self.media_player.positionChanged.connect(self._on_position_changed)
        self.position_slider.sliderMoved.connect(self._on_slider_moved)
        self.position_slider.sliderPressed.connect(self._on_slider_pressed)
        self.position_slider.sliderReleased.connect(self._on_slider_released)

        return

    def _build_counters(self):
        """Create the segment and transcript error counters.

        Returns:
            A :class:`QHBoxLayout` with two :class:`QSpinBox` widgets for
            segment errors and transcript errors.
        """
        layout = QHBoxLayout()

        for attr, label_text in (
            ("seg_spin", "Segment Errors (← / →)"),
            ("trans_spin", "Transcript Errors (↓ / ↑)"),
        ):
            box = QVBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: 500; color: #333333;")
            box.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)

            spin = QSpinBox()
            spin.setRange(0, 100)
            spin.setFixedSize(90, 50)
            spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spin.valueChanged.connect(self._mark_dirty)
            box.addWidget(spin, alignment=Qt.AlignmentFlag.AlignHCenter)
            setattr(self, attr, spin)

            layout.addLayout(box, 1)

        return layout

    def _build_nav(self):
        """Create the navigation controls.

        Returns:
            A :class:`QHBoxLayout` with Previous and Save/Next buttons.
        """
        layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setMinimumHeight(45)
        self.prev_btn.setStyleSheet(COMMON_BUTTON_STYLE)
        self.prev_btn.clicked.connect(self.prev_item)

        self.save_next_btn = QPushButton("Save / Next (Enter)")
        self.save_next_btn.setMinimumHeight(45)
        self.save_next_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.save_next_btn.clicked.connect(self.save_and_next)

        layout.addWidget(self.prev_btn)
        layout.addWidget(self.save_next_btn)

        return layout

    def _init_shortcuts(self):
        """Register keyboard shortcuts for playback and navigation.

        Shortcuts:
            - ``Space``: toggle play/pause
            - ``R``: replay from start
            - ``Return/Enter``: save and next
            - ``Left/Right``: decrease/increase segment errors
            - ``Down/Up``: decrease/increase transcript errors
        """
        QShortcut(QKeySequence("Space"), self, activated=self.toggle_play_pause)
        QShortcut(QKeySequence("R"), self, activated=self.replay_audio)
        QShortcut(QKeySequence("Return"), self, activated=self.save_and_next)
        QShortcut(QKeySequence("Enter"), self, activated=self.save_and_next)
        QShortcut(QKeySequence("Left"), self, activated=lambda: self._adjust_seg(-1))
        QShortcut(QKeySequence("Right"), self, activated=lambda: self._adjust_seg(+1))
        QShortcut(QKeySequence("Down"), self, activated=lambda: self._adjust_trans(-1))
        QShortcut(QKeySequence("Up"), self, activated=lambda: self._adjust_trans(+1))

        return

    def _set_controls_enabled(self, enabled):
        """Enable or disable all player and navigation controls.

        Args:
            enabled: ``True`` to enable controls, ``False`` to disable.
        """
        for w in (
            self.play_btn,
            self.pause_btn,
            self.replay_btn,
            self.save_next_btn,
            self.prev_btn,
            self.position_slider,
        ):
            w.setEnabled(enabled)

        return

    def _wav_name(self, idx):
        """Build the WAV filename for a segment at the given index.

        Args:
            idx: Row index in the DataFrame.

        Returns:
            The WAV filename as ``"<file_name>_<segment_id>.wav"``.
        """
        row = self.df.iloc[idx]

        return f"{row[COL_FILE]}_{str(row[COL_SEG]).strip()}.wav"

    def _audio_path(self, idx):
        """Build the full path to the WAV file for a segment.

        Args:
            idx: Row index in the DataFrame.

        Returns:
            The full :class:`Path` to the WAV audio file.
        """

        return self.paths.audio_dir / self._wav_name(idx)

    def _is_done(self, idx):
        """Check whether a segment has already been validated.

        Args:
            idx: Row index in the DataFrame.

        Returns:
            ``True`` if the segment's ``validated`` column equals 1.
        """

        return int(self.df.iloc[idx].get(COL_VALIDATED, 0)) == 1

    def _list_label(self, idx):
        """Create a formatted list item label with a status icon.

        Args:
            idx: Row index in the DataFrame.

        Returns:
            A string with ``✓`` for validated segments, ``⚠`` for missing
            audio, or the plain WAV filename.
        """
        wav = self._wav_name(idx)
        if not self._audio_path(idx).exists():
            return f"⚠ {wav}"
        if self._is_done(idx):
            return f"✓ {wav}"

        return wav

    def _populate_list(self):
        """Populate the list widget with segment labels from the DataFrame."""
        self.list_widget.clear()
        for i in range(len(self.df)):
            self.list_widget.addItem(QListWidgetItem(self._list_label(i)))

        return

    def _update_list_item(self, idx):
        """Refresh the label of a single list item after validation changes.

        Args:
            idx: Row index of the segment to update.
        """
        item = self.list_widget.item(idx)
        if item:
            item.setText(self._list_label(idx))

        return

    def _go_to(self, idx):
        """Navigate the UI to a specific segment index.

        Args:
            idx: Target row index in the DataFrame.
        """
        self.current_index = idx
        self._refresh_ui()
        self.list_widget.blockSignals(True)
        self.list_widget.setCurrentRow(idx)
        self.list_widget.blockSignals(False)

        return

    def _mark_dirty(self):
        """Set the dirty flag to indicate unsaved changes."""
        self.dirty = True

        return

    def _handle_dirty(self):
        """Resolve unsaved changes before navigation.

        If the dirty flag is set, prompts the user to save, discard, or
        cancel. Saves the row if the user agrees.

        Returns:
            A :attr:`DirtyAction` constant indicating the outcome.
        """
        if not self.dirty:
            return DirtyAction.CLEAN

        r = self._ask_save_before_continue()

        if r == QMessageBox.StandardButton.Cancel:
            return DirtyAction.CANCELLED

        if r == QMessageBox.StandardButton.Yes:
            self._save_row()
            self._update_list_item(self.current_index)
            return DirtyAction.SAVED

        self.dirty = False

        return DirtyAction.DISCARDED

    def _ask_save_before_continue(self):
        """Show a confirmation dialog for unsaved changes.

        Returns:
            The :class:`QMessageBox.StandardButton` chosen by the user
            (Yes, No, or Cancel).
        """
        return QMessageBox.question(
            self,
            "Unsaved changes",
            "You have unsaved changes.\nSave before continuing?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
        )

    def _save_row(self):
        """Save the current segment's error counts to the DataFrame and disk.

        Marks the segment as validated and writes the output TSV atomically.
        """
        self.df.at[self.current_index, COL_ERR_SEG] = int(self.seg_spin.value())
        self.df.at[self.current_index, COL_ERR_TRANS] = int(self.trans_spin.value())
        self.df.at[self.current_index, COL_VALIDATED] = 1
        save_validated_tsv_atomic(self.df, self.paths.output_path)
        self.dirty = False

        return

    def _refresh_ui(self):
        """Refresh the UI to display the current segment's data.

        Updates the header, transcript, audio player, and error counters.
        Resets the dirty flag.
        """
        row = self.df.iloc[self.current_index]

        self._update_header()
        self._update_transcript(row)
        self._load_current_audio()
        self._restore_spin_values(row)

        self.dirty = False

        return

    def _update_header(self):
        """Update the progress and current-file labels for the current index."""
        self.status_label.setText(f"Progress: {self.current_index + 1} / {len(self.df)}")
        self.file_label.setText(f"Current File: {self._wav_name(self.current_index)}")

        return

    def _update_transcript(self, row):
        """Display the transcript text for the current segment.

        Args:
            row: The current pandas Series row from the DataFrame.
        """
        self.transcript_view.setText(str(row[COL_TRANS]))

        return

    def _load_current_audio(self):
        """Load the audio file for the current segment into the media player.

        If the audio file is missing, disables controls and shows a warning hint.
        """
        audio_path = self._audio_path(self.current_index)

        if audio_path.exists():
            self.hint_label.setText("")
            self._set_controls_enabled(True)
            self.media_player.setSource(QUrl.fromLocalFile(str(audio_path)))
        else:
            self.hint_label.setText(f"⚠ Audio file not found: {audio_path}")
            self._set_controls_enabled(False)
            self.media_player.setSource(QUrl())
            with QSignalBlocker(self.position_slider):
                self.position_slider.setRange(0, 0)
                self.position_slider.setValue(0)
            self.time_label.setText("00:00 / 00:00")

        return

    def _restore_spin_values(self, row):
        """Restore the spinbox values from the DataFrame row.

        Signals are blocked during restoration to avoid triggering the
        dirty-state handler.

        Args:
            row: The current pandas Series row from the DataFrame.
        """
        self.seg_spin.blockSignals(True)
        self.trans_spin.blockSignals(True)

        self.seg_spin.setValue(int(row[COL_ERR_SEG]))
        self.trans_spin.setValue(int(row[COL_ERR_TRANS]))

        self.seg_spin.blockSignals(False)
        self.trans_spin.blockSignals(False)

        return

    def _on_duration_changed(self, duration_ms):
        """Handle audio duration changes (Qt slot).

        Updates the seek bar range and enables/disables it based on
        whether a source is loaded.

        Args:
            duration_ms: New audio duration in milliseconds.
        """
        duration_ms = max(0, int(duration_ms))
        with QSignalBlocker(self.position_slider):
            self.position_slider.setRange(0, duration_ms)
        self.position_slider.setEnabled(
            duration_ms > 0 and not self.media_player.source().isEmpty()
        )
        self._update_time_label(self.media_player.position(), duration_ms)

        return

    def _on_position_changed(self, position_ms):
        """Handle playback position changes (Qt slot).

        Updates the seek bar position unless the user is currently dragging it.

        Args:
            position_ms: Current playback position in milliseconds.
        """
        position_ms = max(0, int(position_ms))
        if not self._is_user_seeking:
            with QSignalBlocker(self.position_slider):
                self.position_slider.setValue(position_ms)
        self._update_time_label(position_ms, self.media_player.duration())

        return

    def _on_slider_pressed(self):
        """Handle slider press: enable user-seeking state."""
        self._is_user_seeking = True

        return

    def _on_slider_released(self):
        """Handle slider release: disable user-seeking state and seek to position."""
        self._is_user_seeking = False
        self.media_player.setPosition(int(self.position_slider.value()))

        return

    def _on_slider_moved(self, value_ms):
        """Handle slider drag: seek the audio to the slider value.

        Args:
            value_ms: New slider position in milliseconds.
        """
        self.media_player.setPosition(int(value_ms))

        return

    def _update_time_label(self, pos_ms, dur_ms):
        """Update the time label with the current position and duration.

        Args:
            pos_ms: Current playback position in milliseconds.
            dur_ms: Total audio duration in milliseconds.
        """
        self.time_label.setText(
            f"{format_ms(max(0, int(pos_ms)))} / {format_ms(max(0, int(dur_ms)))}"
        )

        return

    def play_audio(self):
        """Start audio playback from the current position."""
        if not self.media_player.source().isEmpty():
            self.media_player.play()

        return

    def pause_audio(self):
        """Pause audio playback."""
        if not self.media_player.source().isEmpty():
            self.media_player.pause()

        return

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if self.media_player.source().isEmpty():
            return
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

        return

    def replay_audio(self):
        """Restart audio playback from the beginning."""
        if not self.media_player.source().isEmpty():
            self.media_player.setPosition(0)
            self.media_player.play()

        return

    def _adjust_seg(self, delta):
        """Adjust the segment error count by a delta value.

        Args:
            delta: Integer amount to add to the segment error counter
                (positive or negative).
        """
        self.seg_spin.setValue(
            max(
                self.seg_spin.minimum(),
                min(self.seg_spin.maximum(), self.seg_spin.value() + delta),
            )
        )

        return

    def _adjust_trans(self, delta):
        """Adjust the transcript error count by a delta value.

        Args:
            delta: Integer amount to add to the transcript error counter
                (positive or negative).
        """
        self.trans_spin.setValue(
            max(
                self.trans_spin.minimum(),
                min(self.trans_spin.maximum(), self.trans_spin.value() + delta),
            )
        )

        return

    def jump_to_index(self, new_idx):
        """Jump to a segment selected from the list (Qt slot).

        Handles dirty-state resolution before navigating.

        Args:
            new_idx: Target row index in the DataFrame.
        """
        if new_idx < 0 or new_idx >= len(self.df):
            return

        result = self._handle_dirty()
        if result == DirtyAction.CANCELLED:
            self.list_widget.blockSignals(True)
            self.list_widget.setCurrentRow(self.current_index)
            self.list_widget.blockSignals(False)
            return

        self._go_to(new_idx)

        return

    def save_and_next(self):
        """Save the current segment and move to the next one.

        If this is the last segment, triggers the validation summary.
        """
        self._save_row()
        self._update_list_item(self.current_index)

        if self.current_index >= len(self.df) - 1:
            self._finish_validation()
        else:
            self._go_to(self.current_index + 1)

        return

    def _finish_validation(self):
        """Show the final validation summary and offer optional audio cleanup.

        Displays total segment and transcript error counts, then asks
        whether to delete the temporary audio files.
        """
        total_seg, total_trans = compute_totals(self.df)

        QMessageBox.information(
            self,
            "Final Summary",
            f"All data saved!\n\n"
            f"Output: {self.paths.output_path}\n\n"
            f"Total Segment Errors : {total_seg}\n"
            f"Total Transcript Errors: {total_trans}",
        )

        r = QMessageBox.question(
            self,
            "Clean up",
            "Delete audio segments from validation folder?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if r == QMessageBox.StandardButton.Yes:
            self._cleanup_audio_dir()

        return

    def _cleanup_audio_dir(self):
        """Stop playback and remove the temporary audio directory."""
        self.media_player.stop()
        self.media_player.setSource(QUrl())

        if self.paths.audio_dir.exists() and self.paths.audio_dir.is_dir():
            shutil.rmtree(self.paths.audio_dir)

        return

    def prev_item(self):
        """Navigate to the previous segment.

        Handles dirty-state resolution before moving.
        """
        if self.current_index <= 0:
            return
        if self._handle_dirty() == DirtyAction.CANCELLED:
            return
        self._go_to(self.current_index - 1)

        return

    def closeEvent(self, event):  # noqa: N802
        """Handle window close event: resolve unsaved changes before closing.

        If the user cancels, the close event is ignored.
        """
        result = self._handle_dirty()
        if result == DirtyAction.CANCELLED:
            event.ignore()
            return
        if result == DirtyAction.SAVED:
            pass  # already saved inside _handle_dirty
        event.accept()
