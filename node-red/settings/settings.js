const adminAuth = process.env.NODE_RED_ADMIN_PASSWORD_HASH
  ? {
      type: "credentials",
      users: [
        {
          username: process.env.NODE_RED_ADMIN_USER || "admin",
          password: process.env.NODE_RED_ADMIN_PASSWORD_HASH,
          permissions: "*"
        }
      ]
    }
  : undefined;

module.exports = {
  flowFile: "flows/notifications.json",
  credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET || false,
  httpAdminRoot: "/node-red-admin",
  httpNodeRoot: "/node-red",
  adminAuth,
  disableEditor: process.env.NODE_RED_DISABLE_EDITOR === "true",
  functionGlobalContext: {},
  logging: {
    console: {
      level: process.env.NODE_RED_LOG_LEVEL || "info",
      metrics: false,
      audit: true
    }
  }
};
