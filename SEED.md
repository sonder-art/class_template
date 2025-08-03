
This is a template github repository for classes. It will contain some basic information and even some general and basic modules, but it most work as a template.

The repository will be used by technical and non technical people as such we need to keep things really ordered, contained, easy, and automatic. Additionally it most be compatible or easy to use by coding agents.

## Directory Structure
Assume the github repository in the root of the project, i will use relative paths.
The professor directory will be the source or base project. It will contain everything necessary for the web page to render to gitpages, keep everything there nad lets leave the root directory as clean as possible. Lets call that directory `/professor`.

Then we will have an other directory `/students` that will contain the students work. Each student will create their own directory inside `/students` and will contain their own work. Each student will have their own directory, the directory must be named after the student's github username. So if the student github user name is 'uumami' the directory must be named `/students/uumami`. Students will only work inside their own directory, is not allowed to work outside of their own directory.

The students will fork the repository and will work inside their own directory. We need add CI/CD to control the pushes to the github repository for pushing and pull-request to the professor repository (not priority now). More important is that if there is a folder in the `students/' named like the student's github username then the github pages will be rendered with the student's work or that directory. The idea is that it will automatically render the student's work when the student pushes to their github repository. Yet for testing the professor may even have a directory there that may cause confusion, as such we need to add a way to ignore the directory when rendering the github pages, we can have a file in the root directory called 'dna.yml' that contains values we will use for general management, one of those can be professor_profile, in that case that directory will be ignored from the 'students/' by the the ci/cd for rendering.

Example: dna.yml has the following values:

```yaml
professor_profile: uumami
```

Then the ci/cd will ignore the directory `/students/uumami` when rendering the github pages. And instead render the folder with that name in the root. So for uumami, there will be a folder `/uumami` in the root that will be rendered that is the main page. Each students directory is a self-contained complete project, that is the principle.

That dna.yml file will have more values that we can use, this is just the introduction. Like the main repository url, and such.

Professors will work in the `/professor` directory, rememeber that profesor directory will be changed to the professor's github username, we are just using it as a placeholder. Is not optimal but is part of the lore of the repo, to keep it fun.

We will have a script (one of many, we will need some master scripts that do alot of automatic things to keep things clean) that wen ran it will go and see the variable in the dna.yml file for the `professor_profile` and bring the relevant code or data to the students directory. Professors will generaly update, work, change, add and do a lot of things in the `/professor` directory, and students need to "fetch" those things from the professors directory (aside from the repo). think the professor adds a new module or such, we need to automate that sync, yet we need to make smart (waht to bring what not and how, more on that later). Also we should not overwrite the students work, we should only bring the new things to the students directory, if there was a file there, and the student worked over it then overwritting it will break things so we need to be smart about that, do not overwrite. Later, not priority, we can use some diff to merge them or create some way for the student to specify their notes like with some decorator or sintaxt but that is for later. We will define this later in detail and as we advance. Note this is different from the fetch and merge (pull) from github. The idea is to contain everyting the students does to their repository, professor can work everywhere else.

Since students may not be technical, we need to keep things really simple and ordered. As such the files, directories, code, else on the root will be minimal, exposing just the necessary to the students and basic abstractions. Inside certain directories things can go es complex as needed, but the root should be kept simple and the directories used by the students.

AS such i will just focus on the professor directory, since the students directory is just a copy of the professor directory that is managed. The themes, code, and more complex things will be in the professor directory, but copied directly to the students directory that way we can ad improve things without breaking the students work.

## Stack
The stack will be hugo and jupyter-lite. Notes or content will be markdow, juoyter notebooks, jupyter-light in the markdown, .py. The idea is to create a kind of 'framework' for the students to work in and professors to use for their classes. The code for the framework will be in python, hugo, js or what ever is needed. Think of the template as that as a framework. We will ened latex, jupyterlite for running code on the browser, etc.

## Framework
The framework needs to manage things automatically, like the rendering of the website, the sync of the professor and students directories, y, the sync of the jupyter notebooks, the sync of the python code, the sync of the markdown, the sync of the latex, the sync of the jupyter-lite, the sync of the other files, etc.

But also force structure for automation, like indexing, nesting, places where the content will be and such. Headers for the files and content to automate more things, callouts, special strings or decorators or macros to automate or specify things.

Automatic component creation based in structure and such. For example, if i order things in certain way and name them in certain way we can automate generation of components, like a table of contents, a list of files, a list of directories, a list of links, a list of images, a list of videos, a list of audios, a list of other files, etc. Like we run certain things before the hugo rendering to generate content or components or code and such. This is a complete framework, right now is a github template repository that is the aim, later we can see packages and such.

## Content
The content will be a mixture of markdown, jupyter notebooks, jupyter-lite, python. Since this is for classes, we can have really complex code in the ,py that may never be exposed in the final website (but referenced), or actually it would be good to expose it. But we may have lots of contentn code that is just plain .py and such becaus enotebooks and things are not always the best for certain things and helps things ordered and such.

## Structure
professor/
    + class_notes/ # Class notes, markdown, jupyter notebooks, jupyter-lite, python, etc. Basically the main content.
    + framework_code/ # Framework code, python, hugo, js, etc. Students wont work on this directory, but will use it sisnce they need it in order to make their sutendets personal directory a self contained project. Some students may want to add things to the framework code, but that is not the main focus, the main focus is to make the students directory a self contained project. Like their own themes or other things, that is ok but lets not focus on that.
    + framework_documentation/ # Framework documentation, markdown, jupyter notebooks, jupyter-lite, python, etc. This is the documentation for the framework code. How to contribute how to use it etc. Basically the documentation for the framework code. Focused more on the technical side of things for the framework code.
    + framework_tutorials/ # Framework tutorials, markdown, jupyter notebooks, jupyter-lite, python, etc. This is the tutorials for the framework code. How to use it etc. Basically the tutorials for the framework code. Focused more on the practical side of things for the framework code for the students to use.
    + I dont know the best practice of where to put the components, but i think they should be separated from the framework code, the framework code is out automatizations and other relevant things, we probably need to save things in '/professor/components' and then use them in the framework code. but i dont knwo how hugo renders things and such so we need to figure that out correctly.
    + other relevant files like master files for hugo and such, or some global variables for framework code, or for edition.

Think of the use case, a professro will fork the template and start the class form tehre. So giving access to mzster files that can be easily modified to adapt the repository to the class would be great. So organizing and making things easy to change and adapt to the class is a design criteria.

### Content Stucture
Each major category: framework_tutorials, framework_documentation, class_notes, homework, etc. Will have their own directory and structure that will be ensted and hierarchical. As an example:
class_notes/ #category
    + 01_introduction/ # chapter
        + 00_index.md # index automatically generated
        + 01_introduction.md # section
        + 01_a_code_for_introduction.py
        + 01_b_code_for_introduction.py
        + 01_c_code_for_introduction.ipynb
        + 02_testing.md
        + 03_new_concept.md
        + 03_a_code_for_new_concept.py
        + hw_01.md
        + hw_01_a_code_for_hw_01.py
    + 02_testing/
    ...
    + A_advanced_topics/ 
        + 1_advanced_topics.md
        + 1_a_code_for_1_advanced_topics.py
    + 00_master_index.md # master index automatically generated

This example has only one level of nesting, but we can have more levels of nesting, and we can have more levels of nesting for the files and directories. Letters a,b,c will be used for the code files, and numbers for the other files.They follow numbering and letter order taht way we know how to parse it and know what to do with them, rememeber the aim is automation so knowing that hierarchical required structure, the numbering and types of files is a must in order to generate thigns automatically, know how to present them, how to read them, they particularities. We can add speciallized strings or decorators (macros) to each file so we can use them differently. For example the top of the md can have their title, type, date, author, etc so it is taken an used directly, specially by components and other automations.

Capital letters are used for appendices they could be a section of a chapter, or a chapter itself. They follow the same structure as the chapters, but are at the end.

One speciall thing will be a homeowrk file, which will have the prefix hw for code and other files. If added to the class_notes and using the automations it should parse it and add it to some component, page or link the homework directory automatically. The homework category on the navigation bar should display homeworks automatically

Each category (class_notes, framework_tutorials, framework_documentation, homework, etc) will be mapped to the navigation bar and as such it has to be ordered and added automatically. The navigation bar for each category needs to present the information in an easy and simple way for the students or people use, understand and navigate them. We need to think about it, but i think that a collapsable accordion is really good for this, but we can think about it. This is  automatically generated given the imposed instructures in class_notes, framework_documentation, framework_tutorials, homework, etc. Rememeber homework is a special case, it is in class_notes, and thus also generated from there but also has its own category in the navigation bar to allow easy access and usage.



## Templates / Styles
The part of styles and templates must be configurable and organized, for the professor to add, or their students. It must be in a way that students can create their own templates (following the same structure and naming conventions) and use them in their own directory.

For taht is important to maintain a clean and simple structure, and to make things easy to change and adapt to the class, and offer widgets or components that can be easily adapted to other templates or styles.

We need to simplify the templates so they are minimal and easy to understand and use, and creating and new one would be fairly easy.


## Components
We need a top navigation bar with the main pages, like course/class_notes, framework tutorials, homework, etc.

### Componetns for pages
Components for pages: we need a way to make navigating the pages easily and simple. I sugegst (we can think further) to automatically add arrows to go to the next or previous page based on the structure of the pages. I would suggest some collapsable canvas panel that can be used to display the content of the page, and the arrows to go to the next or previous page, also arrows in the end.

We need to think more deeply about this, i want an easy way to move trough the page content, and also trought the sections of the current chapter they are in, we need to think how to do that, what is or are the best ux/ui decisions for achieving this and generate them automatically. Remember we can add macros/headers, strings to delimit or decorators to the files to make them easier to parse and use them automatically or add extra things.

For example each chapter should have an index taht is automatically generated and displayed using 00_index.md for that chapter, also a master index for all chapters and sections that is automatically generated and displayed using 00_master_index.md and they will be at the same level as the categories (the master indices). We can add metadata on the header of each file in a correct way (like yaml or other md) to add a field where we can add an small sentence that will be added to the index generated automatically. Thinhs like that in general to improve quality of life but also allow other things.

### Framework Things
For example adding some special string in a way that if something is between those strings will never be replaced or modified by the framework, or if something is between those strings will be replaced or modified by the framework. This is useful for things like code blocks, or other things that we want to keep as is. rememeber we dont force updates to the files that alreeady exists, but if somewnat wnats it can add what text should be left like that if it is between those strings or the other wya around if something from the base template needs to be added forcibaly i put them between those strings and will be added even if the file was alredy there. This creates and issue because is like a diff or merging files, so lets keep it simple and a simple strategy.

Also having automatic search by keywords and a search on the search bar that is easy and simple. So the tags could be added on the ehader and/or automatically generated from the content and maybe added to the header.

We can use rich and other things to keep things ordered

I would also want to dipslay the code in a nice way (the py and ipynb) in the rendered web page, taht is easy to read and such.

## General things
Keep this usable for students, we run 1 script to automate the generation things, we can have more speciallized scripts, code and things that the master calls it but we can have it clearly separated and easy to use and clean. WE can use sh and python and such, also print things correctly using rich and such, make it really user friendly and easy to use. Lets think more and deeply about this.

Display simple things, and think about general use, avoid students to do things that are not necessary, and make things easy and simple, alsow show possible errros or things overwritten.

Also it must be cimpatible with agentinc coding like cursor and such, documentation and everything should be easy to understand and use. We can even add agentic files, or ven a category aimed for that.. But i think that we can add specific tutotrials, instructions, etc... in the documetnation aimed for agents, they can be directly embeeded in the documentation and such.



