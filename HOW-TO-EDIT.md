# How to edit your website

You can do everything on the GitHub website. No software to install.

Your site: https://evannguyen922.github.io/evan-profile/
Your files: https://github.com/evannguyen922/evan-profile

## The basic steps (works for any file)

1. Open your files link above and click the file you want to change.
2. Click the **pencil icon** (top right of the file) to edit.
3. Make your changes.
4. Click the green **Commit changes** button, then **Commit changes** again.
5. Wait about 1 to 2 minutes, then refresh your site. It rebuilds by itself.

To check that it worked, open the **Actions** tab. A green check means the site is updated. A red X means something went wrong; undo your last change and try again.

## What each file is

- `home.md`: your home page (name, headline, LinkedIn link, bio and resume).
- `posts/`: your 4 blog posts, one file each.
- `images/`: your headshot and any pictures for your posts.

Leave `build.py`, `style.css` and the `.github` folder alone. They run the site.

## Filling in the blanks

Anything that still needs your real details shows up **highlighted in yellow** on the site.
In the files, look for `[ADD: ...]` and `WRITE HERE`. Replace the whole thing, brackets included.

Text between `<!--` and `-->` is a note to you. It never appears on the site. You can delete it.

## Your home page (`home.md`)

The top part, between the two `---` lines, holds:

- `name`, `headline` and `photo`
- `linkedin`: paste your full LinkedIn profile link here
- `tags`: the small labels under your headline, separated by `|`

Under that, the first paragraphs are your bio. Each line starting with `## ` begins a new resume card (Education, Experience, and so on). Each `### ` line is one school, job or club.

Don't add your home address, phone number or anything private. Everyone can see this site.

## Writing a blog post

Open a file in `posts/`. The top part sets the post's details:

- `title`: the post's title
- `date`: written as year-month-day, like `2026-11-20`. Newest posts show first.
- `summary`: one or two sentences shown on the Blog page

Then replace each `WRITE HERE` with your writing. Keep paragraphs short (2 to 4 sentences) and put a blank line between paragraphs.

### Formatting cheat sheet

| You type | You get |
| --- | --- |
| `## My heading` | A section heading |
| `### Smaller heading` | A smaller heading |
| `**bold words**` | **bold words** |
| `*italic words*` | *italic words* |
| `[Text people click](https://website.com)` | A link |
| `- item` at the start of a line | A bullet point |

### Adding a picture with a caption

1. Open the `images` folder, click **Add file**, then **Upload files**, and upload your picture.
   Use a simple file name with no spaces, like `audit-chart.jpg`.
2. In your post, change `placeholder.svg` to your file's name.
3. Keep the two lines together with no blank line between them:

```
![Short description of the picture](images/audit-chart.jpg)
*What the picture shows. Source: [Website name](https://link-to-where-you-found-it)*
```

The first line is the picture. The second line is the caption, and its link credits the source (clicking the picture opens it too).
Only use pictures you're allowed to share, such as your own photos or charts, or free images from sites like Unsplash or Pexels, and always credit them.

### Sources

Each post ends with a `## Sources` list. The links there are starting ideas. Replace them with the exact articles you used, one per line:

```
- [Name of the article or page](https://link-to-it)
```

### Adding another post later

Open `posts/`, click **Add file**, then **Create new file**. Name it something like `5-my-new-post.md`, copy the top part (`---` through `---`) from another post, and write.

## Changing your headshot

Upload a new picture to `images/` with the same name, `headshot.jpg`, and it will replace the old one. A square photo works best.
Your original photo, with its original background, is saved as `images/headshot-original.webp`.
