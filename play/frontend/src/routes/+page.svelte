<script lang="ts">
  import { onMount } from 'svelte';
  import SessionForm from '$lib/components/SessionForm.svelte';
  import SessionItem from '$lib/components/SessionItem.svelte';
  import { sessions, isLoading, error, loadSessions } from '$lib/stores/sessionStore';

  let totalMinutes = 0;

  // Calculate total reading time whenever sessions change
  $: {
    totalMinutes = $sessions.reduce((total, session) => total + session.duration, 0);
  }

  // Format total time as hours and minutes
  $: totalTimeFormatted = formatTotalTime(totalMinutes);

  function formatTotalTime(minutes: number): string {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    if (hours === 0) {
      return `${minutes} minutes`;
    } else if (remainingMinutes === 0) {
      return `${hours} hour${hours !== 1 ? 's' : ''}`;
    } else {
      return `${hours} hour${hours !== 1 ? 's' : ''} and ${remainingMinutes} minute${remainingMinutes !== 1 ? 's' : ''}`;
    }
  }

  onMount(() => {
    loadSessions();
  });
</script>

<svelte:head>
  <title>Reading Tracker</title>
</svelte:head>

<div class="container">
  <header>
    <h1>Reading Tracker</h1>
    <p class="subtitle">Track your daily reading sessions</p>
  </header>

  <main>
    <SessionForm />

    <div class="sessions-container">
      <div class="sessions-header">
        <h2>Your Reading Sessions</h2>
        {#if $sessions.length > 0}
          <div class="stats">
            <p>Total reading time: <strong>{totalTimeFormatted}</strong></p>
            <p>Total sessions: <strong>{$sessions.length}</strong></p>
          </div>
        {/if}
      </div>

      {#if $isLoading}
        <div class="loading">Loading sessions...</div>
      {:else if $error}
        <div class="error">
          <p>Error: {$error}</p>
          <button on:click={loadSessions}>Try Again</button>
        </div>
      {:else if $sessions.length === 0}
        <div class="empty-state">
          <p>You haven't logged any reading sessions yet.</p>
          <p>Use the form above to add your first session!</p>
        </div>
      {:else}
        <div class="sessions-list">
          {#each $sessions as session (session.id)}
            <SessionItem {session} />
          {/each}
        </div>
      {/if}
    </div>
  </main>

  <footer>
    <p>&copy; {new Date().getFullYear()} Reading Tracker App</p>
  </footer>
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  }

  header {
    text-align: center;
    margin-bottom: 32px;
  }

  h1 {
    font-size: 2.5rem;
    color: #333;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 1.2rem;
    color: #666;
    margin-top: 0;
  }

  .sessions-container {
    margin-top: 32px;
  }

  .sessions-header {
    display: flex;
    flex-direction: column;
    margin-bottom: 16px;
  }

  .sessions-header h2 {
    margin-bottom: 8px;
    color: #333;
  }

  .stats {
    background-color: #f0f8ff;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 16px;
  }

  .stats p {
    margin: 4px 0;
  }

  .loading {
    text-align: center;
    padding: 24px;
    color: #666;
  }

  .error {
    background-color: #ffebee;
    color: #c62828;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    text-align: center;
  }

  .error button {
    background-color: #c62828;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 8px;
  }

  .empty-state {
    text-align: center;
    padding: 32px;
    background-color: #f9f9f9;
    border-radius: 8px;
    color: #666;
  }

  footer {
    margin-top: 48px;
    text-align: center;
    color: #666;
    font-size: 0.9rem;
  }
</style>
