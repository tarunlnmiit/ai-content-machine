async function fetchAllMediumStats() {
  const userId = "57e05ba9f4e3";
  let allEdges = [];
  let cursor = null;
  let page = 1;

  while (true) {
    console.log(`Fetching page ${page}...`);
    const res = await fetch('https://medium.com/_/graphql', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify([{
        operationName: "StatsPostsConnection",
        variables: { userId, first: 50, after: cursor || "" },
        query: `query StatsPostsConnection($userId: ID!, $first: Int!, $after: String!) {
          user(id: $userId) {
            id
            postsConnection(first: $first, after: $after) {
              edges {
                node {
                  id title firstPublishedAt mediumUrl readingTime
                  totalStats { views reads }
                  earnings { total { units nanos currencyCode } }
                  collection { name }
                }
              }
              pageInfo { hasNextPage endCursor }
            }
          }
        }`
      }])
    });

    const data = await res.json();
    const conn = data[0].data.user.postsConnection;
    allEdges.push(...conn.edges);
    console.log(`Got ${allEdges.length} articles so far...`);

    if (!conn.pageInfo.hasNextPage) break;
    cursor = conn.pageInfo.endCursor;
    page++;
    await new Promise(r => setTimeout(r, 300));
  }

  const blob = new Blob([JSON.stringify(allEdges)], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'medium-stats-all.json';
  a.click();
  console.log(`Done! Downloaded ${allEdges.length} articles.`);
}

fetchAllMediumStats();