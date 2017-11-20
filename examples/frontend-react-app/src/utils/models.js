import _ from 'lodash'


export const bindModel = (context) => {
  const model = (path) => {
    const value = _.get(context.state, path, '') || '';

    return {
      value,
      checked: value || false,

      onChange(event) {
        let newValue;
        const originalValue = value;

        if (event == null || typeof event === 'string') {
          newValue = event;
        } else {
          newValue = event.target.type === 'checkbox' ?
            event.target.checked :
            event.target.value;
        }

        const newState = {};
        _.set(newState, path, newValue);

        context.setState(_.merge(context.state, newState));

        if (typeof context.onStateChange === 'function') {
          context.onStateChange(path, newValue, originalValue);
        }
      }
    };
  };
  return model;
}
