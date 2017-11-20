import React from 'react'
import { Button, Modal, Glyphicon, FormControl } from 'react-bootstrap'
import { ModelComponent } from '../../utils/components'


class TodoEditor extends ModelComponent {
  state = {
    key: 'todo'
  }

  render() {
    const { id } = this.props.todo;
    const button = id ?
      <Button onClick={this.open} bsSize="xsmall"><Glyphicon glyph="pencil" /></Button> :
      <Button onClick={this.open} bsStyle="success"><Glyphicon glyph="plus" /> Create todo</Button>;

    return (
      <span>
        {button}

        <Modal show={this.state.showModal} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>{id ? `Todo ${id}`: "New Todo"}</Modal.Title>
          </Modal.Header>

          <Modal.Body>
            {this.messageAlert()}

            <form onSubmit={this.onSubmit}>
              {this.field('todo.title', <FormControl type="text" />)}
              {this.field('todo.tag',
                <FormControl componentClass="select">
                  <option value="">None</option>
                  <option value="red">Red</option>
                  <option value="blue">Blue</option>
                  <option value="orange">Orange</option>
                </FormControl>
              )}
              {this.field('todo.priority', <FormControl type="number" step="1" min="0" pattern="\d+" />)}

              <Button bsStyle="primary" type="submit">Save</Button>
              <Button onClick={this.close}>Cancel</Button>
            </form>
          </Modal.Body>
        </Modal>
      </span>
    )
  }
}

export default TodoEditor;
