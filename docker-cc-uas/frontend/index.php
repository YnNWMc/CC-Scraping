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
        <div id="scrapedUrls" class="card mt-4">
            <div class="card-body">
                <h2 class="card-title">Recently Scraped URLs</h2>
                <div class="table-responsive">
                    <table id="recentlyScrapedTable" class="table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>URL</th>
                                <th>Status</th>
                                <th>Web ID</th>
                                <th>Created At</th>
                            </tr>
                        </thead>
                        <tbody id="recentlyScrapedBody">
                            <!-- Table rows will be dynamically added here -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div class="container mt-5">
        <h1 class="text-center mb-4">Get All From DB</h1>
        <div id="databaseUrls" class="card mt-4">
            <div class="card-body">
                <h2 class="card-title">Database Urls</h2>
                <div class="table-responsive">
                    <table id="urlDBTable" class="table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>URL</th>
                                <th>Status</th>
                                <th>Web ID</th>
                                <th>Created At</th>
                            </tr>
                        </thead>
                        <tbody id="urlDBBody">
                            <!-- Table rows will be dynamically added here -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

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

            // ########## Untuk Datatable Search blm bisa ############
            // Update data tergantung interval
            // Interval dalam ms 1000 ms = 1 detik
            setInterval(updateDataTable, 10000); 
            function updateDataTable() {
                urlDBTable.ajax.reload(null, false); // Reload data from server without resetting page
                recentlyScrapedTable.ajax.reload(null, false); // Reload data from server without resetting page
            }
            var recentlyScrapedTable = $('#recentlyScrapedTable').DataTable({
                serverSide: true,
                processing: true,
                responsive: true,  // Enable responsive feature
                ajax: {
                    
                    url: `http://${host_url}:${port_url}/fetch-recently-scraped`,
                    type: 'GET',
                    data: function(d) {
                        return $.extend({}, d, {
                            draw: d.draw,
                            start: d.start,
                            length: d.length,
                            search: d.search.value
                        });
                    }
                },
                columns: [
                    { data: 'id' },
                    { data: 'url' },
                    { data: 'status' },
                    { data: 'web_id' },
                    { data: 'created_at' }
                ],
                columnDefs: [
                    {
                        targets: 1,
                        render: function(data, type, row) {
                            if (data.length > 50) {
                                return '<span class="truncate-text" title="' + data + '">' + data.substring(0, 47) + '...</span>';
                            } else {
                                return '<span>' + data + '</span>';
                            }
                        }
                    },
                    {
                        targets: 4,
                        render: function(data, type, row) {
                            var createdAt = new Date(data);
                            return createdAt.toLocaleString();
                        }
                    }
                ],
                order: [[4, 'asc']], 
                pageLength: 10,
                lengthMenu: [10, 25, 50, 100],
                paging: true,
                searching: true,
                info: true,
                language: {
                    paginate: {
                        first: 'First',
                        last: 'Last',
                        next: 'Next',
                        previous: 'Previous'
                    },
                    info: 'Showing _START_ to _END_ of _TOTAL_ entries',
                    search: 'Search:'
                }
            });
            
            
            var urlDBTable = $('#urlDBTable').DataTable({
                serverSide: true,
                processing: true,
                responsive: true,  // Enable responsive feature
                ajax: {
                    
                    url: `http://${host_url}:${port_url}/fetch-data`,
                    type: 'GET',
                    data: function(d) {
                        return $.extend({}, d, {
                            draw: d.draw,
                            start: d.start,
                            length: d.length,
                            search: d.search.value
                        });
                    }
                },
                columns: [
                    { data: 'id' },
                    { data: 'url' },
                    { data: 'status' },
                    { data: 'web_id' },
                    { data: 'created_at' }
                ],
                columnDefs: [
                    {
                        targets: 1,
                        render: function(data, type, row) {
                            if (data.length > 50) {
                                return '<span class="truncate-text" title="' + data + '">' + data.substring(0, 47) + '...</span>';
                            } else {
                                return '<span>' + data + '</span>';
                            }
                        }
                    }
                ],
                order: [[4, 'asc']], 
                pageLength: 10,
                lengthMenu: [10, 25, 50, 100],
                paging: true,
                searching: true,
                info: true,
                language: {
                    paginate: {
                        first: 'First',
                        last: 'Last',
                        next: 'Next',
                        previous: 'Previous'
                    },
                    info: 'Showing _START_ to _END_ of _TOTAL_ entries',
                    search: 'Search:'
                }
            });
            
            
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

            // Munculin Modal Full URL (hapus aja kalo ga butuh)
            $('#urlDBTable').on('click', '.truncate-text', function() {
                var url = $(this).attr('title');
                $('#urlModalBody').html('<p>' + url + '</p>');
                $('#urlModal').modal('show');
            });

            // ===== 2 function dibawah ini sek tentatif dipake atau ga =======
            // Function to fetch data from backend
            function fetchDataOnDB() {
                let endpoint =`http://${host_url}:${port_url}`;  // Replace with your backend endpoint

                $.ajax({
                    url: endpoint,
                    type: 'GET',
                    contentType: 'application/json',
                    success: function(data) {
                        console.log('Fetched scraped data successfully:', data);
                        updateUIWithScrapedData(data, 'urlDB');
                    },
                    error: function(xhr, status, error) {
                        console.error('Error fetching scraped data:', error);
                        alert('Error fetching scraped data. Please try again.');
                    }
                });
            }
            // Function to update UI with scraped data
            function updateUIWithScrapedData(data, which = 'urlList') {
                var table = $('#urlDBTable').DataTable(); // Get reference to the DataTable instance
                table.clear().draw(); // Clear existing data from DataTable without redrawing

                data.forEach(item => {
                    // Append new rows to the DataTable
                    table.row.add([
                        item[0],    // ID
                        item[1],    // URL
                        item[2],    // Status
                        item[3],    // Web ID
                        item[4]     // Created At
                    ]).draw(false); // Draw without resetting the table
                });
            }

            
        });
    </script>

    
