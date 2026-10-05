# The Qualtrics Survey Setup

The form should follow a parseable structure to be used by the program. It should include
embedded data, question types, question labels, question names, question texts, etc.
> Note that: Multiple choice questions and multiple form field questions have different
> data structures in the API response and needs to be parsed differently.

## Question Formatting

Qualtircs offers enriched HTML code structure supporting inline styles as well as
seperate css scripts. However, the currently used Python's `fpdf2` module supports
basic rendering from HTML. The whole HTML 5 specification is not supported, and
neither is CSS (see [Supported HTML features](https://py-pdf.github.io/fpdf2/HTML.html)
for details).

For simplicity, use the necessary tags for headings, font weights, slanted, underline,
links, line-breaks, etc. and limit the use of inline styles where possible.

## Question Automation Logics

Qualtrics have JavaScript support over the structured questions to connect custom
scripts for automating, rendering, and improving user experience in the form.

Scripts are highly customizable as needed and can be placed on any questions blocks.
However, it is highly suggested to attach the scripts on the triggering questions
(i.e. when a question is set to YES/NO that will execute the script to modify another
question, put the script on the "YES/NO" question for convenience).

## Question Order

Qualtrics have an unique question ID attached to each question and usually in the
format `QID#`. If questions are re-ordered, then the API generated survey response
has no way to identify the question order.

It is suggested to use the `Tools` dropdown to `Auto-number questions` into
`Sequential` order to store the Questions in sequence. Then adjust the parser to
parse and sort in the sequence.

### Related Qualtrics API docs and response data structures

* [Get Survey](https://api.qualtrics.com/73d7e07ec68b2-get-survey)
* [Retrieve a Survey Response](https://api.qualtrics.com/1179a68b7183c-retrieve-a-survey-response)
* [Start Response Export](https://api.qualtrics.com/6b00592b9c013-start-response-export)
* [Get Response Export Progress](https://api.qualtrics.com/37e6a66f74ab4-get-response-export-progress)
* [Get Response Export File](https://api.qualtrics.com/41296b6f2e828-get-response-export-file)
