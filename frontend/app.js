$(document).ready(function() {
    $('#fetch-news-btn').click(function() {
        $.getJSON('/ml-news', function(response) {
            if (response.status === 'success') {
                loadNews();
            } else {
                alert('Error fetching news: ' + response.message);
            }
        });
    });

    function loadNews() {
        $.getJSON('/ml-news', function(data)
         {
            let newsHtml = '';
            data.forEach(article => {
                newsHtml += `
                    <div class="news-article">
                        <h2>${article.title}</h2>
                        <p><strong>Source:</strong> ${article.source_name}</p>
                        <p>${article.summary || article.text.substring(0, 300) + '...'}</p>
                        <a href="${article.url}" target="_blank">Read more</a>
                    </div>
                `;
            });
            $('#news-container').html(newsHtml);
        });
    }
});