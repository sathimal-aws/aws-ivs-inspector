// -- AWS AMPLIFY CONFIGURATION PARAMETERS --
const AmplifyConfig = {
  Auth: {
    Cognito: {
      userPoolClientId: import.meta.env.VITE_APP_CLIENT_ID,
      //  Amazon Cognito User Pool ID
      userPoolId: `${import.meta.env.VITE_USER_POOL_ID}`,
      // REQUIRED only for Federated Authentication - Amazon Cognito Identity Pool ID
      identityPoolId: `${import.meta.env.VITE_IDENTITY_POOL_ID}`,
      // OPTIONAL - Set to true to use your identity pool's unauthenticated role when user is not logged in
      allowGuestAccess: false,
      signUpVerificationMethod: "code", // 'code' | 'link'
      loginWith: {
        username: "false",
        email: "true", // Optional
        phone: "false", // Optional
      },
    },
  },
};
export { AmplifyConfig };
