import React from 'react'
import { Button, Modal, Glyphicon, FormControl } from 'react-bootstrap'
import { ModelComponent } from '../../utils/components'


class ProfileEditor extends ModelComponent {
  state = {
    key: 'profile'
  }

  render() {
    const { profile: { id }, className, bsStyle, glyph, label } = this.props;
    const createFields = !id ? (
      <div>
        {this.field('profile.username', <FormControl type="text" />)}
        {this.field('profile.password', <FormControl type="password" />)}
      </div>
    ) : null;

    return (
      <span className={className}>
        <Button onClick={this.open} bsStyle={bsStyle}><Glyphicon glyph={glyph} /> {label}</Button>

        <Modal show={this.state.showModal} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>{label}</Modal.Title>
          </Modal.Header>

          <Modal.Body>
            {this.messageAlert()}

            <form onSubmit={this.onSubmit}>
              {createFields}
              {this.field('profile.first_name', <FormControl type="text" />)}
              {this.field('profile.last_name', <FormControl type="text" />)}

              <Button bsStyle="primary" type="submit">Save</Button>
              <Button onClick={this.close}>Cancel</Button>
            </form>
          </Modal.Body>
        </Modal>
      </span>
    )
  }
}

export default ProfileEditor;
