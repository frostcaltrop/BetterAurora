# Better Aurora for UTC+8

## How Does It Work?

This application fetches data from external services such as NOAA, WDC Kyoto, and the University of Reading (along with your ip, to calculate your geomagnetic altitude). It retrieves JSON and PNG files from these sources, processes some of them into charts, and displays the data in an HTML format. **Note:** Ensure that you have access to these websites; otherwise, the application will not be able to retrieve the required data.

## How to Use?

1. Open your terminal/bash and install the necessary dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run `app.py` and ensure the application is running correctly:

   ```bash
   python app.py
   ```

3. Open your browser and go to [http://localhost:5000](http://localhost:5000) to view the application.
