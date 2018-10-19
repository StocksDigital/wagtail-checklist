import Cookies from 'js-cookie'
import { isEditPage, isCreatePage, getCurrentURL } from './utils'

module.exports = {
  checklist: {
    get: () => {
      // Figure out whether we are on a 'create' or 'edit' page,
      let action
      const currentUrl = getCurrentURL()
      if (isEditPage()) {
        action = 'EDIT'
      } else if (isCreatePage()) {
        action = 'CREATE'
      } else {
        console.error(`Current URL ${currentUrl} is not a valid checklist URL`)
        return
      }

      // Read form data
      const form = $('#page-edit-form')
      if (!form) {
        console.error('No form found on page')
        return
      }

      const pageData = form.serializeArray().reduce((acc,val) => {
          acc[val['name']] = val['value']
          return acc
      }, {})

      const body = {
        url: currentUrl,
        action: action,
        page: pageData,
      }

      if (!window.CHECKLIST || !window.CHECKLIST.API_URL) {
        throw Error(`Configuration error: wagtail_checklist could not read window.CHECKLIST: ${window.CHECKLIST}`)
      }

      return fetch(window.CHECKLIST.API_URL, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'X-CSRFToken': Cookies.get('csrftoken'),
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify(body),
      })
      .then(r => {
        if (!r.ok) {
          throw Error(r.statusText)
        }
        return r
      })
      .then(r => r.json())
    }
  }
}
