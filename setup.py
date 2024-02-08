import setuptools
import versioneer

def main():
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
        package_dir={'':"src"},
        packages=setuptools.find_packages("src"),
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: MIT License",
        ],
        python_requires='>=3.6',
        install_requires=requirements,
        entry_points={
            'console_scripts': ['trsproc = trsproc:main']
        },
        keywords=['python', 'transcriber', 'trs', 'transcription', 'textgrid', 'nlp']
)

if __name__ == '__main__':
    main()

