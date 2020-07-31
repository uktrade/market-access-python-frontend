export const getCSRFToken = () => {
  let csrfTokenElements = document.getElementsByName("csrfmiddlewaretoken");
  if (csrfTokenElements.length) {
    return csrfTokenElements[0].value;
  }
}
