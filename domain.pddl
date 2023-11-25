(define (domain general_domain)
 (:requirements :typing :action-costs :negative-preconditions)
 (:types
  	location      		; service areas, points of interest, navigation goals
  	robot         		; your amazing yet powerful robot
  	robject				; robjects to be manipulated by the robot
  	robot_platform		; platform slots for the robot to store robjects
	drawer              ; drawer to store robjects
 )

 (:predicates

	; robot ?r is at location ?l
 	(at ?r - robot ?l - location)

 	; robject ?o is on location ?l
 	(on ?o - robject ?l - location)

 	; robject ?o is stored on robot platform ?rp
 	(stored ?o - robject ?rp - robot_platform)

 	; robot platform ?rp is occupied, yb has 3 free places to store robjects
	(occupied ?rp - robot_platform)

	; gripper ?g is holding robject ?o
	(holding ?r - robot ?o - robject)

	; gripper ?g is free (does not contain robject)
	(gripper_is_free ?r - robot)

	; robject ?o is able to hold other robjects
	(container ?o - robject)

	; robject ?o is inserted inside robject ?h
	(in ?peg - robject ?hole - robject)

	; the robject ?o is heavy and cannot be lifted by the robot
	(heavy ?o - robject)

	; specifies if an robject ?o can be inserted into another robject
	(insertable ?o - robject)

	; an robject ?o is perceived when robject recognition was triggered
	; gets lost if the robot moves the base
	(perceived ?l - location)

	; specifies whether the gripper has opened the drawer ?d
	(opened ?d - drawer)

	; robject ?o is located inside drawer ?d
	(inside ?o - robject ?d - drawer)

	; contents of drawer ?d are perceived
	(perceived_inside ?d - drawer)

	; draw ?d is located at location ?l
	(located_at ?d - drawer ?l - location)

	; robject ?o is large
	(is_large ?o - robject)

	; is robot platform ?rp big enough
	(is_big_enough ?rp - robot_platform)
 )

 (:functions
  	(total-cost) - number
 )

; moves a robot ?r from ?source - location to a ?destination - location
; NOTE : the situation in which the robot arm is in any position before moving
; is not handled at the planning level, hence we advise to always move the arm
; to a folded position, then navigate
 (:action move_base
    :parameters (?r - robot ?source ?destination - location)
    :precondition (and (at ?r ?source)
     				   (gripper_is_free ?r)
     			  )
    :effect (and (not (at ?r ?source))
     			(at ?r ?destination)
     			(not (perceived ?source))
				(not (perceived ?destination))
            	    	(increase (total-cost) 20)
     		 )
 )

 ; perceive an robject ?o which is in a location ?l with a empty gripper ?g
 ; to find the pose of this robject before it can be picked
 (:action perceive
   :parameters (?r - robot ?l - location)
   :precondition 	(and 	(at ?r ?l)
   							(gripper_is_free ?r)
   							(not (perceived ?l))
   					)
   :effect 	(and 	(perceived ?l)
                    (increase (total-cost) 20)
  			)
 )

 ; pick an robject ?o which is inside a location ?l with a free gripper ?g
 ; with robot ?r that is at location ?l
 ; (:action pick
 (:action pick
     :parameters (?r - robot ?l - location ?o - robject)
     :precondition 	(and 	(on ?o ?l)
                      		(at ?r ?l)
                      		(perceived ?l)
                      		(gripper_is_free ?r)
                      		(not (holding ?r ?o))
                      		(not (heavy ?o))
                   	)
     :effect (and  	(holding ?r ?o)
                   	(not (on ?o ?l))
                   	(not (gripper_is_free ?r))
                   	(increase (total-cost) 2)
             )
 )

 (:action place
     :parameters (?r - robot ?l - location ?o - robject)
     :precondition  (and  (at ?r ?l)
                          (holding ?r ?o)
                          (not (on ?o ?l))
                          (not (insertable ?o ))
                          (not (gripper_is_free ?r))
                    )
     :effect (and   (on ?o ?l)
                    (not (holding ?r ?o))
                    (gripper_is_free ?r)
		    		(not (perceived ?l))
                    (increase (total-cost) 2)
             )
 )


 ; stage an robject ?o in a robot platform ?rp which is not occupied with a gripper ?g
 ; which is holding the robject ?o
 (:action stage_general
     :parameters (?r - robot ?rp - robot_platform ?o - robject)
     :precondition 	(and 	(holding ?r ?o)
                      		(not (occupied ?rp))
                            (not (gripper_is_free ?r))
							(not (is_large ?o))
                   	)
     :effect (and  	(not (holding ?r ?o))
	 				     (gripper_is_free ?r)
     			   	     (stored ?o ?rp)
                   	     (occupied ?rp)
                   	     (increase (total-cost) 1)
             )
 )


 (:action stage_large
     :parameters (?r - robot ?rp - robot_platform ?o - robject)
     :precondition 	(and 	(holding ?r ?o)
                      		(not (occupied ?rp))
                            (not (gripper_is_free ?r))
							(is_big_enough ?rp)
							(is_large ?o)
                   	)
     :effect (and  	(not (holding ?r ?o))
	 				     (gripper_is_free ?r)
     			   	     (stored ?o ?rp)
                   	     (occupied ?rp)
                   	     (increase (total-cost) 1)
             )
 )

 ; unstage an robject ?o stored on a robot platform ?rp with a free gripper ?g
 (:action unstage
     :parameters (?r - robot ?rp - robot_platform ?o - robject)
     :precondition 	(and 	(gripper_is_free ?r)
                      		(stored ?o ?rp)
                      		(not (holding ?r ?o))
                   	)
     :effect (and  	(not (gripper_is_free ?r))
     			   	     (not (stored ?o ?rp))
                   	     (not (occupied ?rp))
                   	     (holding ?r ?o)
                   	     (increase (total-cost) 1)
             )
 )

 ; inserts a robject ?o which gripper ?g is holding into another robject ?o at location ?l
 (:action insert
   :parameters (?r - robot ?rp - robot_platform ?l - location ?peg ?hole - robject   )
   :precondition 	(and 	(at ?r ?l)
   							(on ?hole ?l)
   							(container ?hole)
   							;(holding ?g ?peg)
                      		(not (holding ?r ?peg))
   							;(not (gripper_is_free ?g))
                            (gripper_is_free ?r)
                            (stored ?peg ?rp)
   							(not (container ?peg)) ;a container cannot be inserted into a container
   					)
   :effect 	(and 	(not (holding ?r ?peg))
   					(gripper_is_free ?r)
   					(in ?peg ?hole)
   					(on ?peg ?l)
                    (not (stored ?peg ?rp))
                    (not (occupied ?rp))
   					(heavy ?hole)
   					(heavy ?peg) ;it doesn't become heavy but it cannot be picked again
   					(increase (total-cost) 15)
   			)
 )

 ; open a drawer ?d using the robot gripper
 ; with robot ?r that is at location ?draw_loc
 (:action open
     :parameters (?r - robot ?draw_loc - location ?d - drawer)
     :precondition 	(and 	(at ?r ?draw_loc)
	 						(located_at ?d ?draw_loc)
							(perceived ?draw_loc)
                      		(gripper_is_free ?r)
							(not (opened ?d))
                   	)
     :effect (and  	(opened ?d)
                   	(gripper_is_free ?r)
                   	(increase (total-cost) 2)
             )
 )

 ; close a drawer ?d using the robot gripper
 ; with robot ?r that is at location ?draw_loc
 (:action close
     :parameters (?r - robot ?draw_loc - location ?d - drawer)
     :precondition 	(and 	(at ?r ?draw_loc)
	 						(located_at ?d ?draw_loc)
                      		(gripper_is_free ?r)
							(opened ?d)
                   	)
     :effect (and  	(not (opened ?d))
                   	(gripper_is_free ?r)
                   	(increase (total-cost) 2)
             )
 )

; perceive a an robject ?o in a drawer ?d with an empty robot gripper
 ; to find the pose of this robject before it can be picked
 (:action perceive_inside_drawer
   :parameters (?r - robot ?draw_loc - location ?d - drawer)
   :precondition 	(and 	(at ?r ?draw_loc)
							(located_at ?d ?draw_loc)
							(opened ?d)
   							(gripper_is_free ?r)
   							(not (perceived_inside ?d))
   					)
   :effect 	(and 	(perceived_inside ?d)
                    (increase (total-cost) 10)
  			)
 )

 ; pick an robject ?o which is inside a drawer ?d at location ?draw_loc with a free gripper
 ; with robot ?r that is at location ?draw_loc
 (:action pick_from_drawer
     :parameters (?r - robot ?draw_loc - location ?d - drawer ?o - robject)
     :precondition 	(and 	(inside ?o ?d)
                      		(at ?r ?draw_loc)
							(located_at ?d ?draw_loc)
                      		(perceived_inside ?d)
                      		(gripper_is_free ?r)
                      		(not (holding ?r ?o))
                      		(not (heavy ?o))
							(opened ?d)
                   	)
     :effect (and  	(holding ?r ?o)
                   	(not (inside ?o ?d))
                   	(not (gripper_is_free ?r))
                   	(increase (total-cost) 2)
             )
 )

 ; place an robject ?o inside a drawer ?d at location ?drawer
 ; with robot ?r that is at location ?draw_loc
 (:action place_inside_drawer
     :parameters (?r - robot ?draw_loc - location ?d - drawer ?o - robject)
     :precondition  (and  (at ?r ?draw_loc)
	 					  (located_at ?d ?draw_loc)
                          (holding ?r ?o)
						  (perceived ?draw_loc)
                          (not (insertable ?o ))
                          (not (gripper_is_free ?r))
						  (opened ?d)
                    )
     :effect (and   (inside ?o ?d)
                    (not (holding ?r ?o))
                    (gripper_is_free ?r)
                    (increase (total-cost) 2)
             )
 )
 )
