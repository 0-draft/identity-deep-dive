TRACKS := ietf-wimse oauth-wg openid

.PHONY: update weekly $(TRACKS:%=update-%) $(TRACKS:%=weekly-%) new-track new-deep-dive

# Run daily update for all tracks
update: $(TRACKS:%=update-%)

update-%:
	@echo "==> Updating track: $*"
	$(MAKE) -C tracks/$* update

# Run weekly digest for all tracks
weekly: $(TRACKS:%=weekly-%)

weekly-%:
	@echo "==> Weekly digest: $*"
	$(MAKE) -C tracks/$* weekly

# Scaffold a new track
new-track:
	@test -n "$(NAME)" || (echo "Usage: make new-track NAME=<track-name>" && exit 1)
	bash scripts/new-track.sh $(NAME)

# Scaffold a new deep dive
new-deep-dive:
	@test -n "$(TRACK)" -a -n "$(TOPIC)" || (echo "Usage: make new-deep-dive TRACK=<track> TOPIC=<topic>" && exit 1)
	bash scripts/new-deep-dive.sh $(TRACK) $(TOPIC)
