import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name="trsproc",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Gabriele Chignoli",
    author_email="gabriele@elda.org",
    description="A Python library to process Transcriber TRS files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    keywords=['python', 'transcriber', 'trs', 'transcription', 'textgrid', 'nlp']
)

