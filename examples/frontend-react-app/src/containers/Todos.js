import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { BaseComponent } from '../utils/components'
import { TodoList, TodoEditor, TodoMemo } from '../components/todo'
import { todoActions } from '../store'
import './Todos.css'


class Todos extends BaseComponent {
  componentWillMount() {
    this.props.loadTodos();
  }

  onSaveTodo = async(todo) => {
    if (todo.id) {
      await this.props.updateTodo(todo);
    } else {
      await this.props.createTodo(todo);
    }
  }

  onDeleteTodo = async(id) => {
    try {
      await this.props.deleteTodo(id);
    } catch (err) {
      this.setError(err);
    }
  }

  render() {
    return (
      <div className="Todos-Page">
        <div className="Todos-Page-Actions">
          <TodoEditor onSave={this.onSaveTodo} todo={{}} />
          <TodoMemo />
        </div>

        {this.messageAlert()}

        <div className="Todos-Page-List">
          <TodoList todos={this.props.todos} onSave={this.onSaveTodo} onRemove={this.onDeleteTodo} />
        </div>
      </div>
    )
  }
}

const { loadTodos, createTodo, updateTodo, deleteTodo } = todoActions;
export default connect(
  (state, ownProps) => ({todos: state.todo.todos }),
  { loadTodos, createTodo, updateTodo, deleteTodo }
)(withRouter(Todos));
