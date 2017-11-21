import { Selector } from 'testcafe';

fixture `Home Page`
  .page `${process.env.TEST_HOST}`;

test('Contains an empty div', async t => {
  await t
    .expect(Selector('.Home-Page').innerText).eql('');
})

test('Redirects to sign-up page', async t => {
  await t
    .click('.Auth-Box-Signup a');

  const h3 = await Selector('.Signup-Page').find('h3');
  const title = await h3.innerText;

  await t
    .expect(title).eql('Sign up');
})

test('Redirects to sign-in page', async t => {
  await t
    .click('.Auth-Box-Signin a');

  const h3 = await Selector('.Signin-Page').find('h3');
  const title = await h3.innerText;

  await t
    .expect(title).eql('Sign in');
})
