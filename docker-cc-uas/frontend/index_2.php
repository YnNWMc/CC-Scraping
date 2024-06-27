<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard Scrapy</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Include DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="./styles.css" />
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
        <h1 class="text-center mb-4">Queue Dashboard</h1>
        <form id="scrapeForm">
            <div class="mb-3">

                <input type="radio" id="scrape" name="scrape_status" value="on">
                <label for="scraped_on">Scraped On</label><br>
                <input type="radio" id="scrape" name="scrape_status" value="off">
                <label for="scraped_off">Scraped Off</label><br>
            </div>
            <button type="submit" class="btn btn-primary">Update</button>
        </form>

        <div id="scrapedUrls" class="card mt-4">
            <div class="card-body">
                <h2 class="card-title">Queue Scraped URLs</h2>
                <div class="table-responsive">
                    <table id="recentlyScrapedTable" class="table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>URL</th>
                                <th>Status</th>

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





    <!-- Bootstrap JS bundle (popper.js included) -->
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <!-- Include DataTables JavaScript -->
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.25/js/dataTables.bootstrap5.min.js"></script>

    <script>
        $(document).ready(function() {

            const host = "<?php echo getenv("BACKEND_HOST"); ?>";
            const port = <?php echo getenv("BACKEND_PORT"); ?>;
            const host_url = "<?php echo getenv("BACKEND_HOST_URL"); ?>";
            const port_url = <?php echo getenv("BACKEND_PORT_URL"); ?>;
            
            setInterval(updateDataTable, 10000);

            function updateDataTable() {
                if (recentlyScrapedTable) {
                    recentlyScrapedTable.ajax.reload(null, false);
                } else {
                    console.error("DataTable is not initialized.");
                }
            }

            var recentlyScrapedTable = $('#recentlyScrapedTable').DataTable({
                serverSide: true,
                processing: true,
                responsive: true, // Enable responsive feature
                ajax: {
                    url: `http://localhost:5002/geturlqueue`,
                    type: 'GET',
                    dataSrc: function(json) {
                        // Transform the API response to DataTables compatible format
                        var dataSet = [];
                        if (json.URL_QUEUE) {
                            for (var i = 0; i < json.URL_QUEUE.length; i++) {
                                dataSet.push({
                                    URL: json.URL_QUEUE[i],
                                    Status: json.scraping_status
                                });
                            }
                        }
                        return dataSet; // Return the transformed data
                    },
                },
                columns: [{
                        data: 'URL'
                    },
                    {
                        data: 'Status'
                    }
                ],
                columnDefs: [{
                        targets: 0,
                        render: function(data, type, row) {
                            // If data is too long, truncate it
                            if (data.length > 50) {
                                return '<span class="truncate-text" title="' + data + '">' + data.substring(0, 47) + '...</span>';
                            } else {
                                return '<span>' + data + '</span>';
                            }
                        }
                    },
                    {
                        targets: 1,
                        render: function(data, type, row) {
                            // Display scraping status
                            return '<span>' + data + '</span>';
                        }
                    }
                ],
                order: [
                    [0, 'asc']
                ],
                pageLength: 10,
                lengthMenu: [10, 25, 50, 100],
                paging: false,
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
                let scrapeStatus = $('input[name="scrape_status"]:checked').val();
                console.log(scrapeStatus);

                $.ajax({
                    url: 'http://localhost:5002/changestatus',
                    type: 'PUT',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        status: scrapeStatus
                    }),
                    success: function(data) {
                        console.log('Scraping initiated:', data);
                        $('#scrapingMessage').text('Scraping initiated. Please wait for results.');
                        $('#stopScraping').show(); // Show stop button if needed
                    },
                });
            });


            function updateUIWithScrapedData(data, which = 'urlList') {
                var table = $('#urlDBTable').DataTable(); // Get reference to the DataTable instance
                table.clear().draw(); // Clear existing data from DataTable without redrawing

                data.forEach(item => {
                    // Append new rows to the DataTable
                    table.row.add([
                        item[0], // ID
                        item[1], // URL
                        item[2], // Status
                        item[3], // Web ID
                        item[4] // Created At
                    ]).draw(false); // Draw without resetting the table
                });
            }
        });
    </script>