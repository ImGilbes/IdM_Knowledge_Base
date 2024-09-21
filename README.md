## TODOs
1. expand to more connected entities ✅
2. references hovering buttons
3. top of spefic page add starting entity entry ✅
4. change name at the beginning of the table into the actual entity ✅
5. landing page graph, picture, buttons, definitions 
6. add description of the function of the page at the beginning of each page
7. add button for showing/hiding filters
8. filter data for specific groups! like for RPs, OPs, idk something else
   1. presets like STRIDE and LINDDUN?
9. feedback proving + request adding entries for entities (they reqest entry, i get it, approve it, then update) you can do it through a pull request
10. Legal protection for users & protection of users' rights -  in the requriements generates an error
   1.  some other entries generate this error, investigate it
11. when displaying the connected entities and entries in specific: add the shared flags (or highlight them) ✅
12. highlight shared flags in specific ✅
13. style the paragraphs and page titles
14. filter data in the index page for categories! ✅
15. filter data for row/category value ✅
16. don't reload the tables in index on every button close and reopen ✅
17. add filters to the specific page ✅
18. allow entries in the specific page to go to their own specific page (recursive specific) ✅
19. add more entities!
    1.  start by adding goals ✅
    2.  add issues ✅
    3.  add limitations ✅
    4.  add more links!
    5.  fill in attacks, vulnerabilities, architectures
20. Replace T and F with checkmarks and crosses (but if possible only in the css) ✅
21. style filters menu ✅
22. solve issue with row filtering and new content of the cells ✅
23. You might wanna rethink how connections are made 

---
When you add a new entity you have to:
1. add the button in index and rename the ids
2. add it to connections map
3. add it to cleanup_df

---
Express formally connection formula in SQL.
Extend the kind of queries!
   modulate the way you build connections
Setup the user experience and use cases

landing page to define use cases

act as someone designing an NDID for the first time
use cases:
   - op, rp
   - system designer
   - user
     - users on different levels 
     - someone who needs understanding
   - regulations compliance

---
## Methodology

#### Collecting the Literature
1. Semi-automated literature review, using a modification of script \<link to script\> available at \<github of the @\>
2. The literature review was conducted on Google Scholar, which comprises \<list databases\>
3. The review was conducted on keywords connected to identity management systems, such as IdM\*, IdP\*, NDID\*, eID\*, and the keywords threat\*, requirement\*, problem\*, issue\*, limitation\*, vulnerability\*, attack\*, mitigation\*, control\*
   1. This list of keywords includes some synonyms that ensured that all relevant literature would be collected
   2. Provide example query
4. The initial number of papers collected was 1200, ~200 after the review
5. Fig a describes shows the steps undertaken during the reviewing process
6. Finally, we integrated the grey literature discovered during the review, bringing the total of relevant literature articles to n

![literature review step](/Methodology_figures/lit%20review%20steps.png "Fig a - Literature Review Steps")

#### Building the Knowledge Framework
1. Analyze existing identity ecosystems to identify relevant entities
2. Define entities with NIST definitions whenever possible
3. Connect entities based on their interactions
4. Validate the framework during the literature review by verifying that all entities are comprised in the framework

![framework](/Methodology_figures/Framework%20v2%20Whole.drawio.png "Resulting Knowledge Framework")

#### Problems with the existing literature
1. Entities wrongly categorized and incorrect application of NIST definitions
2. Little to no information for some entities
3. Incomplete information for most entities

#### Filling the tables
1. Entities are initialized with the analysis of the relevant literature
2. Entities are updated by analyzing the entries of the connected entities!
   1. for entity in knowledge framework:
      1. for connected_entity in connections_of(entity):
         1. for entry in connected_entity:
            1. describe related entity entries
            2. remove duplicates

---

SQL equivalent of the connection query

Provide an SQL query that, given a record of EntityA with an unknown number of booleans fields with value True, returns all the records of EntityB that have those same fields set as True

SELECT *
FROM EntityB b
WHERE EXISTS (
    SELECT 1
    FROM EntityA a
    WHERE a.id = :entityA_id
      AND (a.flag1 = TRUE AND b.flag1 = TRUE OR a.flag1 = FALSE)
      AND (a.flag2 = TRUE AND b.flag2 = TRUE OR a.flag2 = FALSE)
      AND (a.flag3 = TRUE AND b.flag3 = TRUE OR a.flag3 = FALSE)
      ...
      AND (a.flagn = TRUE AND b.flagn = TRUE OR a.flagn = FALSE)
);

---
### Validation
Simulation using the CIE v1
**Goals of CIE**
Security

**Requirements of Cie**
securing communication channel
mutual authentication for communication parties
data interoperability
identification
authentication

**Mitigations of CIE**


**Tasks**
Starting from **Goals**: see what requirements can be found
Starting from **Requirements**: see which mitigations are required and what issues and limitations apply
Starting from **Mitigations**: see which threat are mitigated and which are not.

|Encourage user trust in the system|goal|
|Security|goal|
|mutual communication party authentication|requirement|
|secure communication channel|requirement|
|trust and compliance mark|requirement|
|eCard data portability|requirement|
|eCard data and chip interoperability|requirement|
|eCard: use specialized middleware for cryptographic functionalities|requirement| 


|attacks||
|---|---|
|Personal computer theft| found ✅ | connection to use tls mitigation when investigating the mutual comm party requirement (start) |
|Mobile theft| found ✅ | same as personal computer theft, it is reported as theft of user agent device |
|Card Theft|✅|
|card destruction|✅|
|Man in the Browser|✅|
|Man in the Mobile|✅|
|Social Engineering|already there|
|Shoulder Surfing|✅|
|Eavesdropping knowledge factor for authentication|✅|
|Authenticator duplicator|✅|

Main threats
Spoofing (impersonation)
UnauthZ access through legitimate account
