# LinkedIn post draft -- geometry-based midcurve research topic

Written 2026-08-13 to accompany
`publications/Midcurve_LaTeX/Main_TwoPager_MidcurveNN_GeometryResearch.pdf`.

Deliberately written without em dashes, to match the house style used elsewhere in this repo.
Attach the two-pager PDF to the post, or attach page 1 as an image and link the PDF.

---

## Version A: the main post (recommended)

> I am opening up a research topic, and I am looking for a student to take it on.
>
> Some background. For about six years I have been working on MidcurveNN: teaching a neural
> network to find the midcurve of a 2D shape. It sounds narrow. It is not. Every thin-walled part
> that goes into a structural simulation gets reduced to a simpler idealization first, and in
> production CAD that reduction is still largely done by hand. Automate it well and you save
> engineers real time. Automate it badly and you corrupt the analysis quietly, which is worse.
>
> I have taken this through two full approaches.
>
> The first turned shapes into images and learned image to image. It works, and the output is
> pixels, so you are left with a second unsolved problem: getting a clean polyline back out.
>
> The second turned shapes into JSON text and fine-tuned an LLM on it. This is my best performer
> today. It gives exact coordinates. But it is learning a text convention rather than a geometric
> operation, and it takes a 7 billion parameter model to do something whose actual complexity is
> tiny.
>
> Both of them route a geometry problem through something that is not geometry. So the third
> approach does the obvious thing: represent the shape as a graph, predict the midcurve as a
> graph, exact coordinates throughout.
>
> Here is where it gets interesting, and why I am posting instead of just finishing it.
>
> The model learns roughly where the midcurve points should be. It completely fails to learn how
> they connect. The topology score sits at chance. And that failure is not a hyperparameter I
> forgot to tune. It comes out of four genuinely open questions: how to predict an output set when
> you do not know its size and have no correspondence to the ground truth, how to make topology a
> first class prediction target instead of an afterthought, how to let a network relate two
> opposite walls of a polygon that are far apart in graph distance, and how to claim
> generalization when your dataset has four base shapes.
>
> That is a Master's thesis if you take the first and last of those. It is a PhD if you take all
> four and push into midsurfaces, where the output is not one clean sheet but several meeting at
> non manifold junctions.
>
> What I can offer whoever picks this up: three implemented approaches to benchmark against, a
> working evaluation harness, and an unusually blunt written record of everything currently broken,
> down to file and line numbers. I would rather hand over an honest map than a polished demo.
>
> Two page summary is attached. Code and data are public at github.com/yogeshhk/MidcurveNN
>
> If you are a student looking for a topic, or a supervisor who wants to co-supervise one, get in
> touch.
>
> #MachineLearning #GeometricDeepLearning #CAD #CAE #GraphNeuralNetworks #ResearchOpportunity
> #PhD #Engineering

---

## Version B: shorter, if the long one underperforms

> Six years into MidcurveNN, I have hit the interesting kind of wall, so I am turning it into a
> research topic.
>
> The problem: find the midcurve of a 2D shape. Useful because every thin part in a structural
> simulation gets idealized down first, and in production CAD that is still substantially manual.
>
> I have tried it as images (output is pixels, which is a second problem) and as text with a
> fine-tuned LLM (best current result, but it is learning a serialization, not geometry). The
> third approach represents shapes as graphs and predicts graphs.
>
> It learns where the points go. It does not learn how they connect, at all. Topology accuracy is
> at chance.
>
> That gap is four open questions deep: set prediction without known output size or correspondence,
> topology as a real prediction target, long range reasoning across a polygon, and honest
> generalization from very few shapes. Master's scope or PhD scope depending on how many you take.
>
> Everything is public, including a candid list of what is currently broken:
> github.com/yogeshhk/MidcurveNN
>
> Two pager attached. Students and co-supervisors welcome.
>
> #GeometricDeepLearning #MachineLearning #CAD #ResearchOpportunity

---

## Notes for posting

- Lead image: page 1 of the two-pager, or `images/midcurve_as_graph.png` on its own. The
  profile-to-graph figure reads well as a thumbnail; the results grid does not at small size.
- Best posting window for an academic audience is Tuesday to Thursday morning IST.
- If anyone responds seriously, point them straight at
  `src/geometry_based/analysis_report.md` rather than the README. The report is what makes the
  topic concrete, and it is what distinguishes this from a vague "come do research with me" post.
- Worth cross-posting to any CAD/CAE and geometric-deep-learning groups, and to the departments
  that have previously sent project students.
