import ReactDOM from 'react-dom'
import React, { Component } from 'react'

import Modal from './generic/modal'
import ChecklistModal from './modal'

import api from './api'
import { VALIDATION_TYPES } from './constants'
import { debounce, isEditPage, isCreatePage } from './utils'

import styles from './styles/checklist-button.css'

const SECOND = 1000 // ms

class App extends Component {

  constructor(props) {
    super(props)
    // All app state lives in this component
    this.state = {
      modalOpen: false,
      numPassed: 0,
      numFailed: 0,
      hasFailed: false,
      hasErrors: false,
      hasWarnings: false,
      checklist: {},
    }
  }

  componentDidMount() {
    // If the user interacts with the document, then send a debouced API request
    // except when they click the footer - we do not want "publish" clicks to fire this event
    const debouncedFetch = debounce(2 * SECOND)(this.fetchChecklist)
    debouncedFetch()

    const footer = document.querySelector('footer')
    // Event handler for user interaction
    const onChange = e => {
      if (footer.contains(e.target)) return
      // Lock the publish button
      this.updatePublishButton(false)
      debouncedFetch()
    }
    // Fire on click, keypress or paste, anywhere but the footer
    document.addEventListener('click', onChange)
    document.addEventListener('keydown', onChange)
    document.addEventListener('paste', onChange)
  }

  fetchChecklist = () => {
    api.checklist.get()
    .then(data => this.updateChecklist(data.checklist))
    .catch(console.error)
  }

  updatePublishButton = canPublish => {
    const publishBtn = document.querySelector('button[name="action-publish"]')
    if (canPublish) {
      publishBtn.removeAttribute('disabled')
    } else {
      publishBtn.setAttribute('disabled', true)
    }
  }

  updateChecklist = checklist => {
    let numPassed = 0
    let numFailed = 0
    let hasWarnings = false
    let hasFailed = false
    let hasErrors = false

    for (let name in checklist) {
      for (let validation of checklist[name]) {
        if (!validation.hasError && validation.isValid) {
          numPassed += 1
        } else {
          numFailed += 1
        }
        hasErrors |= validation.hasError
        hasFailed |= !validation.isValid && validation.type === VALIDATION_TYPES.ERROR
        hasWarnings |= !validation.isValid && validation.type === VALIDATION_TYPES.WARNING
      }
    }
    // Lock the publish button if there is a failed validation, otherwise unlock it
    this.updatePublishButton(!hasFailed)
    this.setState({
      numPassed: numPassed,
      numFailed: numFailed,
      hasErrors: Boolean(hasErrors),
      hasFailed: Boolean(hasFailed),
      hasWarnings: Boolean(hasWarnings),
      checklist: checklist,
    })
  }

  toggleModal = e => {
    e && e.preventDefault()
    this.setState({ modalOpen: !this.state.modalOpen })
  }

  render() {
    const { modalOpen, numPassed, numFailed, hasErrors, hasFailed, hasWarnings, checklist } = this.state
    let icon
    let errorStyle
    if (hasErrors) {
      icon = 'icon-error.svg'
      errorStyle = styles.error
    }
    else if (hasFailed) {
      icon = 'icon-fail.svg'
      errorStyle = styles.fail
    }
    else if (hasWarnings) {
      icon = 'icon-warning.svg'
      errorStyle = styles.warning
    }
    else {
      icon = 'icon-pass.svg'
      errorStyle = null
    }

    return (
      <div>
        <button
          className={`button ${errorStyle} ${styles.button}`}
          onClick={this.toggleModal}
        >
          <img className={styles.icon} src={`/static/wagtail_checklist/img/${icon}`}/>
          <span className={styles.text}>Checklist {numPassed} / {numPassed + numFailed}</span>
        </button>
        {modalOpen && (
          <Modal handleClose={this.toggleModal}>
            <ChecklistModal checklist={checklist} numPassed={numPassed} numFailed={numFailed}/>
          </Modal>
        )}
      </div>
    )
  }
}


// If we're creating or editing a page, then render the app in the admin footer.
if (isEditPage() || isCreatePage()) {
  const previewEl = document.querySelector('footer li.preview')
  const appEl = document.createElement('li')
  appEl.id = 'checklist-app'
  previewEl.insertAdjacentElement('beforeBegin', appEl)
  ReactDOM.render(<App/>, appEl)
}
