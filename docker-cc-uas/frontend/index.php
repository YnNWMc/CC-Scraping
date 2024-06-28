<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Indexing</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Include DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="./styles.css"  />
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.25/css/dataTables.bootstrap5.min.css">
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">


    <!-- Modal for displaying full URL -->
    <div class="modal fade" id="urlModal" tabindex="-1" aria-labelledby="urlModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="urlModalLabel">Full URL</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body" id="urlModalBody">
                    <!-- URL content will be inserted here -->
                </div>
            </div>
        </div>
    </div>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Search Indexing</h1>
        <form id="scrapeForm">
            <div class="mb-3">
                <label for="url" class="form-label">Enter URL Seed to Scrape:</label>
                <input type="text" id="url" name="url" class="form-control" required>
            </div>
            
            <button onclick="window.location.href='index_2.php'" type="submit" class="btn btn-primary">Start Scraping</button>
        </form>
        

    <!-- Bootstrap JS bundle (popper.js included) -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <!-- Include DataTables JavaScript -->
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.25/js/dataTables.bootstrap5.min.js"></script>

    <script>
        const host = "<?php echo getenv("BACKEND_HOST"); ?>";
        const port = <?php echo getenv("BACKEND_PORT"); ?>;
        const host_url = "<?php echo getenv("BACKEND_HOST_URL"); ?>";
        const port_url = <?php echo getenv("BACKEND_PORT_URL"); ?>;
        $(document).ready(function() {

            // Event listener for form submit
            $('#scrapeForm').submit(function(event) {
                event.preventDefault();
                let url = $('#url').val();

                $.ajax({
                    url: `http://${host}:${port}/scrape`,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ url: url }),
                    success: function(data) {
                        console.log('Scraping initiated:', data);
                        $('#scrapingMessage').text('Scraping initiated. Please wait for results.');
                        $('#stopScraping').show(); // Show stop button if needed
                    },
                    error: function(xhr, status, error) {
                        let fetchInfo = {
                            endpoint: `http://${host}:${port}/scrape`,
                            method: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({ url: url })
                        };
                        console.log('Fetch information:', fetchInfo);
                        console.error('Error initiating scraping:', error);
                        console.log('XHR status:', xhr.status);
                        console.log('XHR response:', xhr.responseText);
                        alert('Error initiating scraping. Please try again.');
                    }
                });
            });

            // Event listener for stop button
            $('#stopScraping').click(function() {
                stopScraping();
            });

            // Function to stop scraping
            function stopScraping() {
                
                let endpoint = `http://${host}:${port}/stop-scraping`;  // Replace with your Flask server URL

                $.ajax({
                    url: endpoint,
                    type: 'GET',
                    success: function(data) {
                        console.log('Scraping stopped successfully:', data);
                        $('#scrapingMessage').text('Scraping stopped.');
                        $('#stopScraping').hide();
                    },
                    error: function(xhr, status, error) {
                        let fetchInfo = {
                            endpoint: `http://${host}:${port}/stop-scraping`,
                            method: 'GET'
                        };
                        console.log('Fetch information:', fetchInfo);
                        console.error('Error stopping scraping:', error);
                        console.log('XHR status:', xhr.status);
                        console.log('XHR response:', xhr.responseText);
                        alert('Error stopping scraping. Please try again.');
                    }
                });
            }

            


            
        });
    </script>

    
