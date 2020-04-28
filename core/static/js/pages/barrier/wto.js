ma.pages.barrier.wto = (function(){

    function setupAttachments(selector, fieldName){

        if( !( ma.components.FileUpload && ma.components.Attachments && ma.components.AttachmentForm && ma.components.TextArea && jessie.hasFeatures(
            'queryOne', 'cancelDefault', 'getElementData'
        ) ) ){ return; }

        var fileUpload;
        var attachments;

        try {

            fileUpload = new ma.components.FileUpload( {
                group: selector + ' .js-form-group',
                input: selector + ' .js-file-input',
                limitText: selector + ' .js-max-file-size'
            } );
        } catch( e ) { return; }

        var submitButton = jessie.queryOne( '.js-submit-button' );
        var form = fileUpload.form;

        if( !submitButton ){ throw new Error( 'Submit button not found' ); }
        if( !form ){ throw new Error( 'No form found' ); }

        try {

            attachments = new ma.components.Attachments( fileUpload, selector, fieldName );
            new ma.components.AttachmentForm( fileUpload, attachments, submitButton, false );

        } catch( e ){ return; }

        return form;
    }

    return function(){

        setupAttachments(".committee_notification_document_container", "committee_notification_document_id");
        setupAttachments(".meeting_minutes_container", "meeting_minutes_id");

        if( ma.components.DeleteModal ){
            new ma.components.DeleteModal();
        }
    };
})();
