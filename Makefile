NAME=kernel-unity
VER=4
PATCHVER=12
SUBVER=7
DISTREL=1
VERSION=$(VER).$(PATCHVER).$(SUBVER)-$(DISTREL)
PATCHFULLVER=$(VER).$(PATCHVER).$(SUBVER)
KERVER=$(VER).$(PATCHVER)

RPMBUILD=$(shell which rpmbuild)
CAT=$(shell which cat)
SED=$(shell which sed)
RM=$(shell which rm)
WGET=$(shell which wget)

all:

$(NAME).spec: $(NAME).spec.in
	@$(CAT) $(NAME).spec.in | \
		$(SED) -e 's,@VER@,$(VER),g' | \
		$(SED) -e 's,@PATCHVER@,$(PATCHVER),g'| \
		$(SED) -e 's,@SUBVER@,$(SUBVER),g' | \
		$(SED) -e 's,@DISTREL@,$(DISTREL),g' \
			>$(NAME).spec
	@echo
	@echo "$(NAME).spec generated in $$PWD"
	@echo

spec: $(NAME).spec

get:
	@echo
	@echo "Downloading Kernel Source & Kernel Patch"
	@echo
	@$(WGET) https://cdn.kernel.org/pub/linux/kernel/v$(VER).x/linux-$(KERVER).tar.xz
	@$(WGET) https://cdn.kernel.org/pub/linux/kernel/v$(VER).x/linux-$(KERVER).tar.sign 
	@$(WGET) https://cdn.kernel.org/pub/linux/kernel/v$(VER).x/patch-$(PATCHFULLVER).xz
	@$(WGET) https://cdn.kernel.org/pub/linux/kernel/v$(VER).x/patch-$(PATCHFULLVER).sign
	@echo
	@echo "Downloading Kernel Source & Kernel Patch Finished"
	@echo

srpm_build:
	$(RPMBUILD) "--define" "_sourcedir $(shell pwd)" -bs $(NAME).spec
	@$(RM) -rf SOURCES SPECS BUILD BUILDROOT RPMS

srpm: spec get srpm_build

clean:
	@$(RM) -f *.spec
	@$(RM) -rf SRPMS RPMS SOURCES SPECS BUILD BUILDROOT
	@$(RM) -rf linux-$(KERVER).tar.* patch-$(PATCHFULLVER).*
	@find -name '*~' -exec $(RM) {} \;
	@echo
	@echo "Cleaning complete"
	@echo
