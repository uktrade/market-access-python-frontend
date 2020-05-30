const Vue = require( 'vue' ).default;
const Typeahead = require( './typeahead.vue' ).default;

const vueWrappers = Array.from( document.querySelectorAll( '.js-vue-typeahead' ) );

function getOptionsAndRemoveList( parent ){

	const formGroup = parent.querySelector( '.govuk-form-group' );
	const inputs = formGroup.querySelectorAll( 'input' );
	const data = [];

	for( let input of Array.from( inputs ) ){

		if( input.value === '' ){ continue; }

		data.push( { value: input.value, text: input.nextElementSibling.innerText, selected: input.checked } );
	}

	parent.removeChild( formGroup );

	return data;
}

vueWrappers.forEach( ( wrapper ) => {

	const options = getOptionsAndRemoveList( wrapper ); //call this first as it removes the current list from the DOM
	const vm = new Vue({
		el: wrapper,
		components: {
			'typeahead': Typeahead,
		},
	});

	vm.$children[ 0 ].setOptions( options );
});
