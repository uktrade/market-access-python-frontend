ma.pages.barrier.archive = function(){

    if( !ma.components.ConditionalRadioContent ){ return; }

    new ma.components.ConditionalRadioContent({
        inputContainer: '.reason',
        inputName: 'reason',
        conditionalElem: '#conditional-DUPLICATE',
        shouldShow: function( value ){ return ( value === 'DUPLICATE' ); }
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: '.reason',
        inputName: 'reason',
        conditionalElem: '#conditional-NOTABARRIER',
        shouldShow: function( value ){ return ( value === 'NOTABARRIER' ); }
    });

    new ma.components.ConditionalRadioContent({
        inputContainer: '.reason',
        inputName: 'reason',
        conditionalElem: '#conditional-OTHER',
        shouldShow: function( value ){ return ( value === 'OTHER' ); }
    });
};
