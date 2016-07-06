function loadData() {

	var $sport = "cricket"

	var $apiKey = 'AIzaSyBXZciFZEY5s_qpEeYi7WJ-Y32I2Mw7PEw';

	var nyTimesUrl = "http://api.nytimes.com/svc/search/v2/articlesearch.json?q=" +
		$sport + "&response-format=jsonp&callback=svc_search_v2_articlesearch&sort=newest&api-key=d781bddc9d95547090d0040cfd9f6bdd:3:74810776"

		$.getJSON(nyTimesUrl, function (data) {
			data.response.docs.forEach(function (article) {
				$('#sport').append('<li class="article">' +
					'<a href=" + article.web_url + ">' + article.headline.main + '</a></p>');
			});
		}).error(function(e) {
		    console.log('New York Times Articles could not be loaded');
		});
	return false;
};

loadData();