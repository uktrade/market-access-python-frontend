ma.xhr2 = (function(){

	var progressEvent = !!(window.ProgressEvent);
	var formData = !!(window.FormData);
	var withCredentials = window.XMLHttpRequest && 'withCredentials' in ( new XMLHttpRequest );

	if( progressEvent && formData && withCredentials ){

		return function(){

			return new XMLHttpRequest();
		};
	}
}());
