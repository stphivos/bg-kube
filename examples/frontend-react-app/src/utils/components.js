import React, { Component } from 'react'
import { Alert } from 'react-bootstrap'
import { FormGroup, ControlLabel } from 'react-bootstrap'
import { bindModel } from './models'


export class BaseComponent extends Component {
  constructor(props) {
    super(props);

    this.state = { lastError: null };
  }

  setError = (err) => {
    this.setState({ lastError: `${err}` });
  }

  clearError = () => {
    this.setState({ lastError: null });
  }

  messageAlert = () => {
    return this.state.lastError ? (
      <Alert bsStyle="danger" onDismiss={this.clearError}>
        <strong>{this.state.lastError}</strong> Update the form and try again.
      </Alert>
    ) : null;
  }

  redirect(path) {
    this.props.history.push(path);
  }
}

export class ModelComponent extends BaseComponent {
  constructor(props) {
    super(props);

    this.model = bindModel(this);
  }

  field = (name, component, addLabel = true) => {
    const last = name.split('.').pop();
    const label = last.charAt(0).toUpperCase() + last.slice(1).replace(/_/g, ' ');
    const targetComponent = React.cloneElement(component, {...this.model(name), className: last});

    return addLabel ? (
      <FormGroup controlId={name}>
        <ControlLabel>{label}</ControlLabel>
        {targetComponent}
      </FormGroup>
    ) : targetComponent;
  }

  open = () => {
    this.setState({ showModal: true, [this.state.key]: Object.assign({}, this.props[this.state.key]) });
  }

  close = () => {
    this.setState({ showModal: false, lastError: null });
  }

  onSubmit = async(evt) => {
    try {
      evt.preventDefault();

      await this.props.onSave(this.state[this.state.key]);

      this.close();
    } catch (err) {
      this.setState({ lastError: err });
    }
  }
}
