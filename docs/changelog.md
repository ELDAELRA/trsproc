# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **RTTM export**: New `rttm` CLI command and `trs_to_rttm()` Python method to export TRS files to NIST-standard RTTM format for speaker diarization. Non-speech segments and segments without speaker attribution are excluded.

### Fixed

- Fix `reportPossiblyUnboundVariable` warnings for `spk_type` and `turn_spk` in `retrieve_contents()` by initializing default values at appropriate scopes.

## [2.1.0] - 2026-04-16

### Added


### Changed


### Fixed



[Unreleased]: https://github.com/ELDAELRA/trsproc/compare/2.1.0...HEAD
[2.1.0]: https://github.com/ELDAELRA/trsproc/releases/tag/2.1.0

