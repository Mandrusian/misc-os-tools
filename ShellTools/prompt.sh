# ╭──────────────────────────────────────────────────────────╮
# │  Beautiful Bash Prompt for Asahi / Fedora                │
# │  ~/.config/bash/prompt.sh                                │
# ╰──────────────────────────────────────────────────────────╯

# ── Colors (256-color, wrapped in \[ \] for readline) ───────
c_reset='\[\e[0m\]'
c_bold='\[\e[1m\]'
c_dim='\[\e[2m\]'
c_red='\[\e[38;5;203m\]'
c_green='\[\e[38;5;114m\]'
c_yellow='\[\e[38;5;221m\]'
c_blue='\[\e[38;5;111m\]'
c_magenta='\[\e[38;5;176m\]'
c_cyan='\[\e[38;5;80m\]'
c_white='\[\e[38;5;255m\]'
c_gray='\[\e[38;5;245m\]'
c_pink='\[\e[38;5;211m\]'

# ── State ───────────────────────────────────────────────────
_prev_cpu_total=0
_prev_cpu_idle=0
_CPU=0
_MEM_USED=0
_MEM_TOTAL=0
_MEM_PCT=0
_BAT_CAP=""
_BAT_ICON=""
_GIT=""
_LA1="0.00"

# ── CPU usage % (delta between prompts) ─────────────────────
_prompt_cpu() {
  local -a s
  read -ra s < /proc/stat
  local idle=${s[4]}
  local total=0 i
  for ((i=1; i<=8; i++)); do (( total += s[i] )); done
  if (( _prev_cpu_total > 0 )); then
    local dt=$(( total - _prev_cpu_total ))
    local di=$(( idle - _prev_cpu_idle ))
    (( dt > 0 )) && _CPU=$(( 100 * (dt - di) / dt ))
  fi
  _prev_cpu_total=$total
  _prev_cpu_idle=$idle
  (( _CPU < 0 ))   && _CPU=0
  (( _CPU > 100 )) && _CPU=100
}

# ── Memory used/total in GB, one decimal (pure bash) ────────
_prompt_mem() {
  local total avail k v u
  while read -r k v u; do
    case $k in
      MemTotal:)     total=$v ;;
      MemAvailable:) avail=$v; break ;;
    esac
  done < /proc/meminfo
  local used_kb=$(( total - avail ))
  _MEM_USED="$(( used_kb / 1048576 )).$(( (used_kb % 1048576) * 10 / 1048576 ))"
  _MEM_TOTAL="$(( total / 1048576 )).$(( (total % 1048576) * 10 / 1048576 ))"
  _MEM_PCT=$(( used_kb * 100 / total ))
}

# ── Battery ─────────────────────────────────────────────────
_prompt_bat() {
  _BAT_CAP=""; _BAT_ICON=""
  local d
  for d in /sys/class/power_supply/BAT* /sys/class/power_supply/macsmc-battery; do
    [[ -d $d ]] || continue
    _BAT_CAP=$(<"$d/capacity")
    case $(<"$d/status") in
      Charging)    _BAT_ICON=" ⚡" ;;
      Full)        _BAT_ICON=" ✓" ;;
      Discharging) _BAT_ICON="" ;;
      *)           _BAT_ICON="" ;;
    esac
    return
  done
}

# ── Load average (1 min) ────────────────────────────────────
_prompt_load() {
  read -r _LA1 _ _ _ _ < /proc/loadavg
}

# ── Git branch + status flags ───────────────────────────────
_prompt_git() {
  _GIT=""
  command -v git >/dev/null 2>&1 || return
  local b
  b=$(git symbolic-ref --short HEAD 2>/dev/null) \
    || b=$(git rev-parse --short HEAD 2>/dev/null) \
    || return
  local d=""
  git diff --quiet --ignore-submodules 2>/dev/null || d+=" ✚"
  git diff --cached --quiet --ignore-submodules 2>/dev/null || d+=" ●"
  [[ -n $(git ls-files --others --exclude-standard 2>/dev/null | head -n1) ]] && d+=" ?"
  local ab
  ab=$(git rev-list --left-right --count '@{u}...HEAD' 2>/dev/null)
  if [[ -n $ab ]]; then
    local behind=${ab%%$'\t'*} ahead=${ab##*$'\t'}
    (( ahead  > 0 )) && d+=" ↑${ahead}"
    (( behind > 0 )) && d+=" ↓${behind}"
  fi
  _GIT="${b}${d}"
}

# ── Threshold color helper ──────────────────────────────────
_pct_color() {
  local p=$1
  if   (( p >= 85 )); then printf '%s' "$c_red"
  elif (( p >= 60 )); then printf '%s' "$c_yellow"
  else                     printf '%s' "$c_green"
  fi
}

# ── Build the prompt ────────────────────────────────────────
_prompt_update() {
  local ec=$?
  _prompt_cpu
  _prompt_mem
  _prompt_bat
  _prompt_load
  _prompt_git

  local cc mc bc=""
  cc=$(_pct_color "$_CPU")
  mc=$(_pct_color "$_MEM_PCT")
  if [[ -n $_BAT_CAP ]]; then
    if   (( _BAT_CAP < 20 )); then bc=$c_red
    elif (( _BAT_CAP < 50 )); then bc=$c_yellow
    else                           bc=$c_green
    fi
  fi

  local ex=""
  (( ec != 0 )) && ex="${c_red}${c_bold}✘ ${ec}${c_reset}"

  local git_str=""
  [[ -n $_GIT ]] && git_str=" ${c_dim}on${c_reset} ${c_yellow}${_GIT}${c_reset}"

  local bat_str=""
  [[ -n $_BAT_CAP ]] && bat_str=" ${c_dim}│${c_reset} ${bc} BAT ${_BAT_CAP}%${_BAT_ICON}${c_reset}"

  PS1="${c_dim}╭─${c_reset}${c_cyan}${c_bold}\u${c_reset}${c_dim}@${c_reset}${c_magenta}${c_bold}\h${c_reset}"
  PS1+=" ${c_dim}in${c_reset} ${c_green}\w${c_reset}"
  PS1+="${git_str}"
  PS1+=$'\n'

  PS1+="${c_dim}├─${c_reset}${c_white}${c_bold}\D{%H:%M:%S}${c_reset}"
  PS1+=" ${c_gray}\D{%Y-%m-%d %a}${c_reset}"
  PS1+=" ${c_dim}│${c_reset} ${cc} CPU ${_CPU}%${c_reset}"
  PS1+=" ${c_dim}│${c_reset} ${mc} RAM ${_MEM_USED}/${_MEM_TOTAL}G${c_reset}"
  PS1+="${bat_str}"
  PS1+=" ${c_dim}│${c_reset} ${c_blue} LD ${_LA1}${c_reset}"
  PS1+=$'\n'

  PS1+="${c_dim}╰─${c_reset}"
  [[ -n $ex ]] && PS1+=" ${ex}"
  PS1+=" ${c_pink}${c_bold}❯${c_reset} "
}

PROMPT_COMMAND=_prompt_update
