import CONSTANTS from './constants'

// Determine whether the current URL matches a Wagtail admin create / edit page URL
const getCurrentURL = () => window.location.href.split('#')[0]
const isEditPage = () => CONSTANTS.EDIT_REGEX.test(getCurrentURL())
const isCreatePage = () => CONSTANTS.CREATE_REGEX.test(getCurrentURL())

// Debounce user input
const debounce = delay => {
  let timer = null
  return func => {
      return (...args) => {
        clearTimeout(timer)
        timer = setTimeout(() => func( ...args), delay)
      }
  }
}


module.exports = {
  debounce,
  getCurrentURL,
  isEditPage,
  isCreatePage,
}
