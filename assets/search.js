const posts = [
  {
    title: "Building a Reading-First Blog",
    summary:
      "A practical breakdown of what makes long-form technical blogs feel calm, readable, and worth returning to.",
    url: "posts/building-a-reading-first-blog.html",
  },
  {
    title: "Shipping Static Sites With Confidence",
    summary:
      "Why a small static deployment surface is often the right tradeoff for a personal site that needs to stay fast and cheap.",
    url: "posts/shipping-static-sites-with-confidence.html",
  },
];

const queryInput = document.querySelector("#query");
const results = document.querySelector("#results");

function render(matches) {
  if (!results) {
    return;
  }

  if (matches.length === 0) {
    results.innerHTML = '<p class="meta">No matching posts yet.</p>';
    return;
  }

  results.innerHTML = matches
    .map(
      (post) => `
        <article class="search-result">
          <h2><a href="${post.url}">${post.title}</a></h2>
          <p>${post.summary}</p>
        </article>
      `
    )
    .join("");
}

if (queryInput) {
  render(posts);

  queryInput.addEventListener("input", (event) => {
    const term = event.target.value.trim().toLowerCase();
    const matches = posts.filter((post) => {
      return (
        post.title.toLowerCase().includes(term) ||
        post.summary.toLowerCase().includes(term)
      );
    });

    render(matches);
  });
}
