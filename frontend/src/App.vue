<template>
  <div>
    <nav style="padding: 1em; border-bottom: 1px solid #ccc">
      <router-link to="/">Transactions</router-link> |
      <router-link to="/log">Add Transaction</router-link>
    </nav>

    <div style="padding: 1em">
      <router-view />
    </div>
  </div>
</template>
