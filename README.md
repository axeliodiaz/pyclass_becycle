# Web Scraping Project

This project is designed to perform web scraping using Python. It leverages lightweight tools like `requests` and `BeautifulSoup` for scraping static web pages and parsing HTML content. The project structure is designed to be simple and modular, making it easy to extend or adapt to different scraping requirements.

## Project Structure

```
.
├── Dockerfile           # Docker configuration for containerizing the project
├── README.md            # Project documentation
├── docker-compose.yml   # Docker Compose file to manage the services
├── requirements.txt     # Python dependencies
├── settings.py          # Project settings and configuration
├── single_version.py    # Main script for executing scraping tasks
└── utils.py             # Utility functions for handling common tasks
```

## Prerequisites

- **Python 3.8 or higher**
- **Docker and Docker Compose** (optional for containerization)
- **Virtualenv** (optional for local virtual environment)

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running Locally
1. Create a virtual environment (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Edit `settings.py` to configure the target URL and any additional settings (e.g., headers, user-agent).
4. Run the main script:
   ```bash
   python single_version.py
   ```
5. The extracted data will be processed and saved based on the logic defined in the script.

### Running with Docker
1. Build the Docker image:
   ```bash
   docker build -t web_scraping_project .
   ```
2. Run the container:
   ```bash
   docker run --rm web_scraping_project
   ```

### Running with Docker Compose
1. Start the services defined in `docker-compose.yml`:
   ```bash
   docker-compose up --build
   ```
2. Stop the services:
   ```bash
   docker-compose down
   ```

### Switching Between Virtualenv and Docker
- If you prefer a local Python environment, use the `virtualenv` setup.
- For isolated, reproducible environments, use Docker or Docker Compose.
- Both approaches can coexist without conflict as long as you manage dependencies correctly.

## Customization

- **Settings:**
  - Update `settings.py` to configure:
    - Target URL
    - Set the maximum consecutive errors wanted (5 by default)
    - Define the starting ID 

---

Feel free to suggest improvements or report issues. Happy scraping! 🚀
