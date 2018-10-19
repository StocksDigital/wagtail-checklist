import React, { Component } from 'react'
import PropTypes from 'prop-types'

import styles from './styles/modal.css'
import { VALIDATION_TYPES } from './constants'


export default class ChecklistModal extends Component {

  static propTypes = {
    numPassed: PropTypes.number,
    numFailed: PropTypes.number,
    checklist: PropTypes.objectOf(
      PropTypes.arrayOf(
        PropTypes.shape({
          type: PropTypes.string,
          isValid: PropTypes.bool,
          hasError: PropTypes.bool,
          message: PropTypes.string,
        })
      )
    ),
  }

  render() {
    const { checklist, numPassed, numFailed } = this.props
    return (
      <div>
        <h2 className={styles.title}>Checklist {numPassed} / {numPassed + numFailed}</h2>
        <div>
          {Object.keys(checklist)
            .sort((a, b) => a <= b ? -1 : 1)  // Sort alphabetically
            .map((name, idx) => <ValidationGroup key={idx} name={name} validations={checklist[name]}/>)
          }
        </div>
      </div>
    )
  }
}


const ValidationGroup = ({name, validations}) => {
  const failedValidations = validations.filter(v => !v.isValid || v.hasError)
  if (failedValidations.length < 1) return null
  return (
    <div className={styles.group}>
      <div className={styles.groupTitle}>{name}</div>
      <div className={styles.list}>
        {failedValidations.map((v, idx) => <ValidationRule key={idx} {...v}/>)}
      </div>
    </div>
  )
}


const ValidationRule = props => (
  <div className={styles.rule}>
    <div className={styles.checkMarkWrapper}><CheckMark {...props}/></div>
    <span className={styles.message}>{props.message}{props.hasError && <ErrorMessage/>}</span>
  </div>
)


const ErrorMessage = () => (
  <span className={styles.ruleError}>
    <br/>a server-side error occurred while checking this rule - tell your system admin
  </span>
)


const CheckMark = props => {
  const isWarning = props.type === VALIDATION_TYPES.WARNING
  let icon
  if (props.hasError) { icon = 'icon-error.svg' }
  else if (props.isValid) { icon = 'icon-pass.svg' }
  else if (isWarning) { icon = 'icon-warning.svg' }
  else { icon = 'icon-fail.svg' }
  return <img className={styles.checkMark} src={`/static/wagtail_checklist/img/${icon}`}/>
}
