# Python File Download Automator
This Python script automatically organizes files in the Downloads folder into subdirectories based on their types (e.g., images, videos, music, documents, etc.). It provides a flexible and customizable solution for organizing cluttered Downloads folders, making it easier to find and manage files.

## Features

- Automatically monitors the Downloads folder for any changes and organizes files accordingly.
- Configurable via a JSON configuration file for customizing directory paths and file extensions.
- Supports organizing files into subdirectories based on their types, such as images, videos, music, and documents.

## Usage

1. Clone or download this repository to your local machine.
2. Ensure you have Python installed on your system.
3. Modify the `config.json` file to specify the desired directory paths and file extensions.
4. Run the `organizer.py` script using Python.
5. Sit back and let the script automatically organize your Downloads folder!

## Configuration

The `config.json` file allows you to customize the behavior of the script:

- `source_dir`: The directory to monitor for file changes (default: Downloads).
- `dest_dir_*`: Destination directories for different file types (default: Downloads/*).
- `*_extensions`: List of file extensions for each file type.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

