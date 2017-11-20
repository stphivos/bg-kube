import React from 'react'
import { ListGroup } from 'react-bootstrap'
import { TodoItem } from '.'


export default (props) => (
  <ListGroup>
    {props.todos.map(todo =>
      <TodoItem key={todo.id}
        todo={todo}
        onSave={props.onSave}
        onRemove={props.onRemove} />
    )}
  </ListGroup>
)
