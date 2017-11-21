import React from 'react'
import { Button, Glyphicon, ListGroupItem } from 'react-bootstrap'
import { TodoEditor } from '.'


export default (props) => (
  <ListGroupItem>
    <Button onClick={() => props.onRemove(props.todo.id)} bsSize="xsmall"><Glyphicon glyph="remove" /></Button>
    <TodoEditor onSave={props.onSave} todo={props.todo} />
    <label className="label" style={{backgroundColor: props.todo.tag || 'gray'}}>{props.todo.title}</label>
  </ListGroupItem>
)
