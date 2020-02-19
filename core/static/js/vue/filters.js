function getString( parentName, text ){

	if( parentName ){

		text = `<span class="parent-text">${ parentName } > </span>${ text }`;
	}

	return text;
}

module.exports = {

	highlight: ( str, words, parentName ) => {

		if( !words ){ return getString( parentName, str ); }

		const queryWords = words.split( ' ' ).filter( ( word ) => word.length >= 1 );
		const openTag = '<span class=\'highlight\'>';
		const closeTag = '</span>';

		queryWords.forEach( ( word ) => {
			const query = new RegExp(`(${word})(?![^<]+?>)`, 'ig');
			str = str.replace( query, ( matchedTxt ) => ( openTag + matchedTxt + closeTag ) );
		});

		return getString( parentName, str );
	}
};
