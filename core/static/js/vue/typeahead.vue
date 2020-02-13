<template>
	<div v-bind:class="classes" v-bind:id="name+'__typeahead'">

		<label class="govuk-label filter-items__label" :for="id">
			{{ label }}
		</label>

		<multiselect
			label="text"
			track-by="value"
			open-direction="bottom"
			v-model="selectedOptions"
			:placeholder="placeholder"
			:clear-on-select="true"
			:close-on-select="false"
			:hide-selected="true"
			:internal-search="false"
			:multiple="true"
			:options="options"
			:options-limit="1000"
			:showLabels="false"
			:searchable="true"
			:id="id"
			@search-change="search">

			<template slot="clear" slot-scope="props">
				<div class="multiselect__clear" v-if="selectedOptions" @mousedown.prevent.stop="clearAll(props.search)"></div>
			</template>

			<template slot="option" slot-scope="props">
				<div class="multiselect__option-label" v-html="$options.filters.highlight(props.option.text, props.search, props.option.parentName)"></div>
			</template>

			<template slot="noResult">
				<span>No results found</span>
			</template>

			<template slot="caret" slot-scope="methods">
				<div v-if="showCaret">
				<div @mousedown.prevent.stop="methods.toggle()" class="multiselect__select"></div>
				</div>
			</template>
		</multiselect>

		<input type="hidden" :name="name"
			v-for="(option, index) in selectedOptions"
			:key="index" :value="option.value">
	</div>
</template>

<script>

	const Multiselect = require( 'vue-multiselect' ).default;
	const { highlight } = require( './filters' );
	const uuid = require( 'uuid/v4' );

	/**
	 * matchWords
	 *
	 * breaks your search query into an array containing a word/character or words/characters
	 * loops through your array and increments a count whenever it gets a match
	 * returns true when the count value matches the array length
	 * Useful when doing a fuzzy search on a string
	 *
	 * @param {string} str is the data to search on
	 * @param {string} words is your query
	 *
	 * @returns {boolean}
	 */

	function matchWords( str, words ){

		const queryWords = words.split( ' ' );
		const count = queryWords.reduce( ( allWords, word ) => {

			if( str.toLowerCase().includes( word.toLowerCase() ) ){
				allWords++;
			}

			return allWords;

		}, 0 );

		return queryWords.length === count;
	}

	export default {
		components: {
			'multiselect': Multiselect,
		},
		props: {
			label: {
				type: String,
				required: true,
			},
			name: {
				type: String,
				required: true,
			},
			placeholder: {
				type: String,
				required: true,
			},
			value: {
				type: String,
				required: false,
				default: ''
			},
			classes: {
				type: String,
				required: false,
			},
		},

		data () {

			return {
				id: uuid(),
				options: [],
				optionsData: [],
				selectedOptions: [],
			};
		},

		filters: {
			highlight
		},

		methods: {

			setOptions: function( options ){

				options.forEach( ( option ) => {

					const token = ' > ';
					const text = option.text;
					const tokenPosition = text.indexOf( token );

					if( tokenPosition > 0 ){

						option.parentName = text.substring( 0, tokenPosition );
						option.text = text.substring( tokenPosition + token.length );
					}
				} );

				this.options = options;
				this.optionsData = options;
				this.selectedOptions = options.filter( ( item ) => item.selected );
			},

			search: function( query ){
				//filter options when typing
				this.options = this.optionsData.filter( ( item ) => {
 					return matchWords( item.text + ( item.parentName || '' ), query );
				})
			},
		},

		computed: {
			showCaret: function(){
				return this.options.length > 0;
			}
		}
	}
</script>
