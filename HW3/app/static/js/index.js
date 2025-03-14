$(document).ready(function () {
    let table = $('#resultsTable').DataTable({
        "pagingType": "simple_numbers",
        "pageLength": 10,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "全部"]],
        "language": {
            "lengthMenu": "顯示 _MENU_ 筆資料",
            "zeroRecords": "找不到相關資料",
            "info": "顯示第 _START_ 至 _END_ 筆，共 _TOTAL_ 筆",
            "infoEmpty": "顯示第 0 至 0 筆，共 0 筆",
            "infoFiltered": "(從 _MAX_ 筆資料中過濾)",
            "search": "搜尋:",
            "paginate": {
                "first": "第一頁",
                "last": "最後一頁",
                "next": "下一頁",
                "previous": "上一頁"
            }
        },
        columnDefs: [
            { targets: 1, className: 'link-column' }
        ]
    });

    let isSearching = false;

    function performSearch() {
        let query = $('#searchQuery').val();
        if (!query || isSearching) return;

        $('#loadingSpinner').show();
        $('#searchBtn').prop('disabled', true);
        isSearching = true;

        $.getJSON(`/api/search?query=${query}`, function (data) {
            table.clear();
            data.results.forEach(item => {
                let shortLink = new URL(item.link).hostname;
                table.row.add([
                    item.title,
                    `<a href="${item.link}" target="_blank" title="${item.link}">${shortLink}</a>`,
                    item.source
                ]);
            });
            table.draw();
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.error("Search failed:", textStatus, errorThrown);
        }).always(function () {
            $('#loadingSpinner').hide();
            $('#searchBtn').prop('disabled', false);
            isSearching = false;
        });
    }

    // 綁定搜尋按鈕點擊事件
    $('#searchBtn').click(performSearch);

    // 綁定 Enter 鍵事件
    $('#searchQuery').keydown(function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            $('#searchBtn').click();
        }
    });
});
