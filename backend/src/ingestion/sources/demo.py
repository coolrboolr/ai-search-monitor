from .base import Source, RawJob

class DemoSource(Source):
    # Note: this source is not wired into the v0 ingestion pipeline; used for local demos/tests only.
    name = "demo"

    async def fetch(self):
        print("Running Demo Source...")
        yield RawJob(
            external_id="demo-1",
            title="AI Search Engineer",
            company="FutureCorp AI",
            location="Remote",
            url="https://example.com/job1",
            source="demo",
            posted_at="2023-10-27",
            description="Build the next generation of search engines using LLMs."
        )
        yield RawJob(
            external_id="demo-2",
            title="SEO Specialist for AI Products",
            company="TechGiant",
            location="San Francisco, CA",
            url="https://example.com/job2",
            source="demo",
            posted_at="2023-10-26",
            description="Optimize our AI product landing pages."
        )
        yield RawJob(
            external_id="demo-3",
            title="Head of Search",
            company="StartupX",
            location="New York, NY",
            url="https://example.com/job3",
            source="demo",
            posted_at="2023-10-25",
            description="Lead our search strategy."
        )
        yield RawJob(
            external_id="demo-4",
            title="Barista",
            company="CoffeeShop",
            location="Seattle, WA",
            url="https://example.com/job4",
            source="demo",
            posted_at="2023-10-24",
            description="Make coffee. Not AI related."
        )
        yield RawJob(
            external_id="demo-5",
            title="Senior Software Engineer, Search Quality",
            company="Google",
            location="Mountain View, CA",
            url="https://example.com/job5",
            source="demo",
            posted_at="2023-10-23",
            description="Improve search quality using large language models and BERT."
        )
