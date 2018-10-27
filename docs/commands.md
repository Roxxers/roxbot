# Command Documentation

## Base Commands
These are the base commands for Roxbot that are a part of the core bot. All of them deal with internal management and are, for the most part, unavalible to average users.

## Cog Commands

### Admin
The Admin cog adds admin commands to Roxbot which should make moderating a Discord server easier.

#### ;slowmode

### Custom Commands

### Fun

#### ;roll

Rolls a die using dice expression format. Spaces in the expression are ignored.

**Command structure**

`;roll expression`

**Aliases**

`die`, `dice`

!!! example "Examples"
    Roll one d10 two times
    
        ;roll d10x2
    
    Output
        
        Roll 1: (8) Totaling: 8    
        Roll 2: (4) Totaling: 4


    Roll two d20s and takes the highest value, then adds 7
    
        ;roll 2d20h1 + 7
    
    Output
    
        Rolled: (10,7) + 7 Totaling: 17


An expression can consist of many sub expressions added together and then a multiplier at the end to indicate how many times the expression should be rolled.

Sub expressions can be of many types:
	
- `[number] #add this number to the total`
- `d[sides] #roll a dice with that many sides and add it to the total`
- `[n]d[sides] #roll n dice. each of those dice have <sides> number of sides, sum all the dice and add to the total`
    - `add r[number] #reroll any rolls below [number]`
    - `add h[number] #only sum the [number] highest rolls rather than all of them`
    - `add l[number] #only sum the [number] lowest rolls rather than all of them`
- `x[number] #only use at the end. roll the rest of the expression [number] times(max 10)`

Credit: TBTerra#5677
		
### Image Editor

### Join Leave

### NSFW

### Reddit

### Self Assign

### Trivia

### Util

### Voice
