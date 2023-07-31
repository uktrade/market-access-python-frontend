ma.components.CharacterCount = (function (doc, jessie) {
    var html =
        jessie.isHostObjectProperty(doc, "documentElement") &&
        doc.documentElement;

    if (
        !(
            jessie.isHostMethod(html, "insertAdjacentElement") &&
            jessie.isHostMethod(html, "insertAdjacentHTML")
        )
    ) {
        return;
    }
    if (
        !jessie.hasFeatures(
            "queryOne",
            "attachListener",
            "bind",
            "addClass",
            "removeClass"
        )
    ) {
        return;
    }

    function CharacterCount(moduleSelector) {
        var $module = jessie.queryOne(moduleSelector);
        this.$module = $module;
        this.$textarea =
            $module && jessie.queryOne(".js-character-count", $module);

        if (!this.$textarea) {
            return;
        }

        // Read options set using dataset ('data-' values)
        this.options = this.getDataset($module);

        // Determine the limit attribute (characters or words)
        var countAttribute = this.defaults.characterCountAttribute;

        if (this.options.maxwords) {
            countAttribute = this.defaults.wordCountAttribute;
        }

        // Save the element limit
        this.maxLength = parseInt($module.getAttribute(countAttribute), 10);

        // Check for limit
        if (!this.maxLength) {
            return;
        }

        // Generate and reference message
        this.countMessage = this.createCountMessage();

        // If there's a maximum length defined and the count message exists
        if (this.countMessage) {
            // Remove hard limit if set
            $module.removeAttribute("maxlength");

            // Bind event changes to the textarea
            this.bindChangeEvents();

            // Update count message
            this.updateCountMessage();
        }
    }

    CharacterCount.prototype.defaults = {
        characterCountAttribute: "data-maxlength",
        wordCountAttribute: "data-maxwords",
    };

    // Read data attributes
    CharacterCount.prototype.getDataset = function (element) {
        var dataset = {};
        var attributes = element.attributes;

        if (attributes) {
            for (var i = 0, l = attributes.length; i < l; i++) {
                var attribute = attributes[i];
                var match = attribute.name.match(/^data-(.+)/);

                if (match) {
                    dataset[match[1]] = attribute.value;
                }
            }
        }

        return dataset;
    };

    // Counts characters or words in text
    CharacterCount.prototype.count = function (text) {
        var length;

        if (this.options.maxwords) {
            var tokens = text.match(/\S+/g) || []; // Matches consecutive non-whitespace chars
            length = tokens.length;
        } else {
            length = text.length;
        }

        return length;
    };

    // Generate count message and bind it to the input
    // returns reference to the generated element
    CharacterCount.prototype.createCountMessage = function () {
        var countElement = this.$textarea;
        var elementId = countElement.id;
        // Check for existing info count message
        var countMessage = document.getElementById(elementId + "-info");

        // If there is no existing info count message we add one right after the field
        if (elementId && !countMessage) {
            countElement.insertAdjacentHTML(
                "afterend",
                '<span id="' +
                    elementId +
                    '-info" class="govuk-hint govuk-character-count__message"></span>'
            );
            this.describedBy = countElement.getAttribute("aria-describedby");
            this.describedByInfo = this.describedBy + " " + elementId + "-info";
            countElement.setAttribute("aria-describedby", this.describedByInfo);
            countMessage = document.getElementById(elementId + "-info");
        } else {
            // If there is an existing info count message we move it right after the field
            countElement.insertAdjacentElement("afterend", countMessage);
        }

        return countMessage;
    };

    // Bind input propertychange to the elements and update based on the change
    CharacterCount.prototype.bindChangeEvents = function () {
        var $textarea = this.$textarea;
        jessie.attachListener(
            $textarea,
            "keyup",
            jessie.bind(this.checkIfValueChanged, this)
        );

        // Bind focus/blur events to start/stop polling
        jessie.attachListener(
            $textarea,
            "focus",
            jessie.bind(this.handleFocus, this)
        );
        jessie.attachListener(
            $textarea,
            "blur",
            jessie.bind(this.handleBlur, this)
        );
    };

    // Speech recognition software such as Dragon NaturallySpeaking will modify the
    // fields by directly changing its `value`. These changes don't trigger events
    // in JavaScript, so we need to poll to handle when and if they occur.
    CharacterCount.prototype.checkIfValueChanged = function () {
        if (!this.$textarea.oldValue) {
            this.$textarea.oldValue = "";
        }

        if (this.$textarea.value !== this.$textarea.oldValue) {
            this.$textarea.oldValue = this.$textarea.value;
            this.updateCountMessage();
        }
    };

    // Update message box
    CharacterCount.prototype.updateCountMessage = function () {
        var countElement = this.$textarea;
        var options = this.options;
        var countMessage = this.countMessage;

        // Determine the remaining number of characters/words
        var currentLength = this.count(countElement.value);
        var maxLength = this.maxLength;
        var remainingNumber = maxLength - currentLength;

        // Set threshold if presented in options
        var thresholdPercent = options.threshold ? options.threshold : 0;
        var thresholdValue = (maxLength * thresholdPercent) / 100;

        if (thresholdValue > currentLength) {
            jessie.addClass(
                countMessage,
                "govuk-character-count__message--disabled"
            );
        } else {
            jessie.removeClass(
                countMessage,
                "govuk-character-count__message--disabled"
            );
        }

        // Update styles
        if (remainingNumber < 0) {
            jessie.addClass(countElement, "govuk-textarea--error");
            jessie.addClass(countMessage, "govuk-error-message");
            jessie.removeClass(countMessage, "govuk-hint");
        } else {
            jessie.removeClass(countElement, "govuk-textarea--error");
            jessie.removeClass(countMessage, "govuk-error-message");
            jessie.addClass(countMessage, "govuk-hint");
        }

        // Update message
        var charVerb = "remaining";
        var charNoun = "character";
        var displayNumber = remainingNumber;

        if (options.maxwords) {
            charNoun = "word";
        }

        charNoun =
            charNoun +
            (remainingNumber === -1 || remainingNumber === 1 ? "" : "s");

        charVerb = remainingNumber < 0 ? "too many" : "remaining";
        displayNumber = Math.abs(remainingNumber);

        countMessage.innerHTML =
            "You have " + displayNumber + " " + charNoun + " " + charVerb;
    };

    CharacterCount.prototype.handleFocus = function () {
        // Check if value changed on focus
        this.valueChecker = setInterval(
            jessie.bind(this.checkIfValueChanged, this),
            1000
        );
    };

    CharacterCount.prototype.handleBlur = function () {
        // Cancel value checking on blur
        clearInterval(this.valueChecker);
    };

    return CharacterCount;
})(document, jessie);
