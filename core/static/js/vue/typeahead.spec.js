const Vue = require( 'vue' ).default;
const { mount } = require( '@vue/test-utils' );
const Typeahead = require( './typeahead.vue' ).default;

describe( 'Typeahead', () => {

	let defaultProps;

	beforeEach(() => {

		defaultProps = {
			name: 'adviser',
			label: 'Adviser',
			placeholder: 'Search adviser',
			classes: 'typeahead-element'
		};
	});

	describe( 'template', () => {

		let component;

		beforeEach(() => {
			component = mount( Typeahead, {
				propsData: defaultProps,
			} );
		});

		describe( 'when rendering default state', () => {
			it( 'should render a control wrapper with the request classes for styling', () => {
				expect( component.find( '.typeahead-element' ).exists() ).toEqual( true );
			});

			it( 'should render the label', () => {
				expect( component.find( '.filter-items__label' ).text() ).toEqual( 'Adviser' );
			});

			it( 'should render a multi select control', () => {
				expect( component.find( 'input.multiselect__input' ).exists() ).toEqual( true );
			});

			it( 'should render a placeholder value in search text field', () => {
				expect( component.find( '.multiselect__input' ).attributes().placeholder ).toEqual( 'Search adviser' );
			});
		});

		describe( 'when there are suggestions to display', () => {
			describe( 'With default data', () => {

				beforeEach( ( done ) => {

					const dataWithOptions = Object.assign( {}, defaultProps, {
						options: [{
							value: '1234',
							text: 'Fred Smith',
						}, {
							value: '4321',
							text: 'Jane Jones',
						}],
					});

					component.setData( dataWithOptions );
					Vue.nextTick( done );
				});

				it( 'should render an item for each option', () => {
					const options = component.findAll( '.multiselect__element .multiselect__option' );
					expect( options.length ).toEqual( 2 );
				});

				it( 'should render the correct markup for an option', () => {
					const markup = component.find( '.multiselect__element .multiselect__option' ).element.innerHTML;
					expect( markup ).toEqual( '<div class="multiselect__option-label">Fred Smith</div>' );
				});
			} );
		});

		describe( 'when advisers are selected', () => {
			beforeEach( ( done ) => {
				const dataWithSelectedAdvisers = Object.assign( {}, defaultProps, {
					selectedOptions: [{
						value: '1234',
						text: 'Fred Jones',
					}],
				});

				component.setData( dataWithSelectedAdvisers );
				Vue.nextTick( done );
			});

			it( 'should populate the default selected options', () => {
				expect( component.findAll( '.multiselect__tag' ).length ).toEqual( 1 );
			});

			it( 'should show the adviser name in the tag', () => {
				expect( component.find( '.multiselect__tag' ).text() ).toEqual( 'Fred Jones' );
			});

			it( 'should render the selected options as hidden fields', () => {
				const element = component.find( 'input[type="hidden"][name="adviser"]' ).element;
				expect( element.value ).toEqual( '1234' );
			});
		});
	});

	describe( 'data', () => {

		let component;

		describe( 'when created with no value', () => {

			beforeEach(() => {

				component = mount( Typeahead, {
					propsData: defaultProps,
				});
			});

			it( 'should set a default of no selected advisers', () => {
				expect( component.vm.selectedOptions ).toEqual( [] );
			});
		});

		describe( 'when created with previously selected advisers', () => {
			describe( 'With simple data', () => {

				let component;
				let defaultOptions;

				beforeEach( () => {

					defaultOptions = [{
						value: '1234',
						text: 'Fred Smith',
					}, {
						value: '4321',
						text: 'Jane Jones',
						selected: true
					}];

					component = mount( Typeahead, {
						propsData: defaultProps,
					});

					component.vm.setOptions( defaultOptions );

				} );

				it( 'should populate the selection options value', () => {
					expect( component.vm.selectedOptions ).toEqual( [ { value: defaultOptions[ 1 ].value, text: defaultOptions[ 1 ].text, selected: true } ] );
				});
			} );

			describe( 'With parent > child data', () => {

				let defaultOptions;
				let component;

				beforeEach( () => {

					defaultOptions = [{
						value: '1234',
						text: 'Country1 > child1',
					}, {
						value: '4321',
						text: 'Country2 > child2',
						selected: true
					}];

					component = mount( Typeahead, {
						propsData: defaultProps,
					});

					component.vm.setOptions( defaultOptions );
				} );

				it( 'Should populate the selection options correctly', () => {

					expect( component.vm.selectedOptions ).toEqual( [ { value: defaultOptions[ 1 ].value, text: 'child2', parentName: 'Country2', selected: true } ] );
				} );

				it( 'should render an item for each option', () => {
					const options = component.findAll( '.multiselect__element .multiselect__option' );
					expect( options.length ).toEqual( 1 );
				});

				it( 'should render the correct markup for an option', () => {
					const markup = component.find( '.multiselect__element .multiselect__option' ).element.innerHTML;
					expect( markup ).toEqual( '<div class="multiselect__option-label"><span class="parent-text">Country1 &gt; </span>child1</div>' );
				});
			} );
		});
	});

	describe( 'methods', () => {
		describe( '#search', () => {

			const wrapper = mount( Typeahead, {
				propsData: {
					name: 'dit_team',
					label: 'Team',
					placeholder: 'Search teams',
				},
			});

			wrapper.vm.setOptions( [{
				"value": "cff02898-9698-e211-a939-e4115bead28a",
				"text": "Aberdeen City Council"
			}, {
				"value": "08c14624-2f50-e311-a56a-e4115bead28a",
				"text": "Advanced Manufacturing Sector"
			}, {
				"value": "d33ade1c-9798-e211-a939-e4115bead28a",
				"text": "Advantage West Midlands (AWM)"
			}] );

			const textInput = wrapper.find( '.multiselect__input' );

			it( 'should have a placeholder with a value', () => {
				expect( textInput.attributes().placeholder ).toEqual( 'Search teams' );
			});

			describe( 'when the user enters a query that has no results', () => {

				beforeEach( () => {
					textInput.setValue( 'cheese' );
				});

				it( 'should not have fetched results', () => {
					const listItem = wrapper.find( '.multiselect__content li' );
					expect( listItem.text() ).toEqual( 'No results found' );
				});
			});

			describe( 'when the user enters a character that matches', () => {

				beforeEach( () => {
					textInput.setValue( 'a' );
				});

				it( 'should have fetched results', () => {
					const listItem = wrapper.find( '.multiselect__content li' );
					expect( listItem.text() ).toEqual( 'Aberdeen City Council' );
				});
			});

			describe( 'when the user enters characters that match', () => {

				beforeEach( () => {
					textInput.setValue( 'aber' );
				});

				it( 'should have fetched results', () => {
					const listItem = wrapper.find( '.multiselect__content li' );
					expect( listItem.text() ).toEqual( 'Aberdeen City Council' );
				});
			});

			describe( 'when the user enters words that match in reverse order', () => {

				beforeEach( () => {
					textInput.setValue( 'City Aberdeen' );
				});

				it( 'should have fetched results', () => {
					const listItem = wrapper.find( '.multiselect__content li' );
					expect (listItem.text() ).toEqual( 'Aberdeen City Council' );
				});
			});

			describe( 'when the user enters words that match in all lowercase', () => {
				beforeEach( () => {
					textInput.setValue( 'aberdeen city' );
				});
				it( 'should have fetched results', () => {
					const listItem = wrapper.find( '.multiselect__content li' );
					expect( listItem.text() ).toEqual( 'Aberdeen City Council' );
				});
			});

			describe( 'when the user enters words that match in all uppercase', () => {
				beforeEach( () => {
					textInput.setValue( 'ABERDEEN CITY' );
				});
				it( 'should have fetched results', () => {
					const listItem = wrapper.find( '.multiselect__content li' );
					expect( listItem.text() ).toEqual( 'Aberdeen City Council' );
				});
			});
		});
	});
});
