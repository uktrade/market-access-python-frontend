export const getCSRFToken = () => {
  let csrfTokenElements = document.getElementsByName("csrfmiddlewaretoken");
  if (csrfTokenElements.length) {
    return csrfTokenElements[0].value;
  }
}


export const getCheckboxValues = (element) => {
  const filterItems = element.getElementsByClassName("checkbox-filter__item")
  let values = []

  for (let i = 0; i < filterItems.length; i++) {
    let item = filterItems[i]
    values.push({
      "value": item.querySelector('input').value,
      "label": item.querySelector('label').textContent.trim(),
      "checked": item.querySelector('input').checked,
    })
  }
  return values
}
