import React from 'react';
import { shallow, mount } from 'enzyme';
import { ProfileEditor } from '..';
import * as mocks from '../../../__mocks__/user'


describe('User', () => {

  describe('Components', () => {

    describe('ProfileEditor', () => {
      const getProps = () => ({
        profile: mocks.getProfile(),
        onSave: () => {},
        className: 'a-css-class',
        bsStyle: 'primary',
        glyph: 'cog',
        label: 'Settings'
      })

      it('Renders without crashing', () => {
        shallow(<ProfileEditor {...getProps()} />);
      })

      it('Contains parent element', () => {
        const obj = getProps();
        const wrapper = shallow(<ProfileEditor {...obj} />);
        expect(wrapper.find(`.${obj.className}`)).toHaveLength(1);
      })

      it('Contains settings button', () => {
        const obj = getProps();
        const wrapper = mount(<ProfileEditor {...obj} />);
        const button = wrapper.find('.btn-primary');
        expect(button).toHaveLength(1);
        expect(button.text()).toEqual(` ${obj.label}`);
      })
    })
  })
})
