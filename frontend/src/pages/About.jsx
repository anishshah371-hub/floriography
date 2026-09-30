function About() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-semibold text-gray-900">About Floriography</h1>

      <section className="mt-6">
        <h2 className="text-lg font-medium text-gray-900">What this is</h2>
        <p className="mt-2 text-gray-700">
          Floriography is an information-retrieval application over a documented
          dataset of flower symbolism. It is not a generative AI product — it never
          invents a flower's meaning. Every result comes directly from the supplied
          dataset, currently 30 records covering 12 communication categories.
        </p>
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-medium text-gray-900">How meaning search works</h2>
        <p className="mt-2 text-gray-700">
          Your query and every record's documented meaning are converted into
          TF-IDF vectors (term frequency × inverse document frequency), and ranked
          by cosine similarity between your query and each record. A word that
          appears in almost every record (like "I" or "love") gets a low weight; a
          distinctive word (like "friendship" or "bashfulness") gets a high one —
          so results are driven by what's actually distinctive about a match, not
          just any shared word.
        </p>
        <p className="mt-2 text-gray-700">
          A simpler keyword-overlap baseline is also implemented and was measured
          against TF-IDF on a small evaluation set built from this dataset —
          TF-IDF improved mean reciprocal rank from 0.667 to 0.812. See{' '}
          <code className="rounded bg-gray-100 px-1 py-0.5 text-sm">docs/SEARCH_METHODOLOGY.md</code>{' '}
          and <code className="rounded bg-gray-100 px-1 py-0.5 text-sm">docs/EVALUATION.md</code> in
          the repository for the full methodology and results.
        </p>
      </section>

      <section className="mt-6">
        <h2 className="text-lg font-medium text-gray-900">Data and honesty</h2>
        <p className="mt-2 text-gray-700">
          The current dataset has no source citations, so none are shown or
          invented. Historical meanings, human-language interpretations, and
          categories are exactly as supplied — raw text is preserved unedited; a
          single documented spelling normalization (for search purposes only) is
          the only cleaning applied.
        </p>
      </section>
    </div>
  )
}

export default About
