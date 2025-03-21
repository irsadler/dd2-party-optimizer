Darkest Dungeon 2 Team Builder
User Guide/Readme
--------

I felt like I would play DD2 more often with my limited gaming time every week if I didn't spend 10 minutes in the crossroads screen before every run, and then I got to thinking that this could be the case for other people also. The app is designed to provide (currently) 2 helpers for designing DD2 parties, in a way that should hopefully speed up the process. It is not designed to take all the brain work out of designing a party, and assumes that users are already at least reasonably familiar with the party comp mechanics in the game.

The backend code for the tool is mainly Python with some light SQL. It deploys as a streamlit app. It is free to download and use or modify (a shoutout would be nice, but I can't force you.)

 The data was collected from tables found on the DD2 game wiki (s/o to them for doing the grind work because this app would not have been developed if I had to copy any data from the game myself.)

-------------------

Report bugs: to the git repo at https://github.com/irsadler/dd2-party-optimizer/issues , please glance thru and make sure yours hasn't already been reported before.

Suggestions for the tool: happy to hear them, feel free to message irene-sadler on discord (please maybe put something like 'suggestion for DD2 app' or something in the subject line so i don't assume you are some kind of strange cold messaging catfish attempt. You can also send message on reddit @bananaguard4.

-------------------
---Tabs---
-----
Tab 1 ('team rater') --
-----
This is a tool that produces a statistical summary of a team of 4 heroes and a general rating of how good that team's stats are. It also returns the stat breakdowns for each hero selected.

 It works by getting the descriptive statistics (mean, st. deviation, quartiles, min/max) for all possible heroes. It then compares the mean of the 4 selected heroes against these values. If the average of a statistic is above the 3rd quartile it labels that value 'high'. If it's below the first quartile it labels the value 'low'. Otherwise, the value is 'average'.

There is an optional toggle to keep Bounty Hunter from being included in the calculations of the descriptive statistics, as his stats trend quite high. It is turned off by default.

You can also choose whether you want to see the team using their upgraded stats, instead of base (in which case it will compare vs. the upgraded stats for all heroes.)

You can also download the team to an Excel spreadsheet for later.

-------
Tab 2 ('build team')---
-------
 This is a tool that tries to create an optimized team for various features one might want a team to be good at. It works via a series of filters and some basic arithmetic, which are applied to the backend data. It will return a view that contains 4 heroes, some breakdown of their specific paths (depending on user input), and a suggested moveset for each hero/path combination. There is a toggle to return either base or mastery upgrade moves (at the moment, it will return solely base or mastery upgrade stats; in future I might find a way to suggest mastery upgrades of some base movesets). You can also download the result to an Excel spreadsheet for later.

Your options for party building are as follows:

1. Decide if you want to exclude any heroes from consideration (for instance, BH or some DLC characters.) This filters out the characters entirely, so not only do they not appear in the results but also they won't be comped against in the backend. This, and your mastery/base stat choice, is the first filter in the order of operations.
2. Select the hero stats and/or resistances you want to try to boost. Note that these are boosted in order of how you select them; for instance if you select 'speed' and 'stun', the tool will first find heroes with high speed, then with high stun. As a result, you may end up with a final party that includes a very fast character with low stun resist and also a scattering of medium speed/stun resist. This choice is applied third overall.
3. Select skill boost. You can pick from damage or crit (or none.) Because skill damage is actually a range of values, the tool will optimize for the mean damage value for each character (so for instance, if you have a skill that does 2-5 damage, you will see the damage value reported as 3.5). This option is applied 2nd, at the same time as the skill effect filter.
4. Select some effects for skills (or none if you don't care). At the moment, the tool doesn't differentiate from whether you are applying, removing, or blocking ('cannot gain') that skill; this is a future step. You have various options of tokens and effects that can be applied. The tool will try to find moves that are associated with at least 1 of any specified token/effect, and then it ranks them by how many each move involves. For instance, if you were looking for blight and/or combo skills, it would likely select the Grave Robber Poison Dart skill, which can apply both. This filter is applied to the data second, in combination with #3.
5. Filter paths. Your options here are 'Wanderer', which returns only the Wanderer path and skill versions for the party, 'Best Available', which will return the best path and path skill versions for each hero it found to fit your filters, or 'Show All', which will return every path for each hero. This filter is applied last.

-------
FYI
-------

Some general things to think about when using the builder tool:

As I mentioned previously, the tool isn't designed to do all the gameplay homework for you, just to speed the crossroads screen process up. Therefore, we assume you have some general idea of how individual heroes individually work and are aware that you shouldn't use eg. Occultist as a position 1 tank. This is also why we don't provide all the details of every skill, just the numerical ones. We assume that for instance you already know that Highwayman Riposte skill has some chance of applying the combo token.

 The tool also only offers suggestions based on those numbers; if you think a different skill in the results loadout is a better choice, use it instead. However, if you don't care or maybe don't have time or interest in carefully curating your own loadouts, you can just pick the ones the tool indicates. Assuming you set up reasonable filters, they should return something viable.
 
Using a lot of filters for skill selection is fine, but only a few may have varying results. Because I decided I always wanted to return 4 heroes, with 5 moves per path, if the tool finds that it didn't suggest enough moves to fill out a full loadout, it will simply select the next skill in order that it didn't already suggest for that hero+path. Applying none is fine, however.

Using too many filters (>3) for stats&resistances may not work so well, because most heroes tend to have pretty similar stat values when you look at resistances and so trying to optimize for too many of them at once will drag parties down to 'average' stats overall.
